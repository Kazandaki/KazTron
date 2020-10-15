from typing import Iterable, Sequence, Dict, Optional, MutableMapping, Set
import secrets
import logging

import praw

from kaztron.config import SectionView, get_kaztron_config, get_runtime_config

logger = logging.getLogger(__name__)


class RedditConfig(SectionView):
    client_id: str
    client_secret: str
    user_agent: str
    refresh_uri: str


class RedditState(SectionView):
    refresh_tokens: MutableMapping[str, Optional[str]]  # username -> refresh_token
    last_auth_state: str


class RedditLoginManager:
    """
    Manages login credentials and OAuth flow for Reddit, and provides instances of the PRAW Reddit
    object that allows Reddit access.

    See `tools/reddit_auth.py` for a usage example.

    KazTron bot extensions can declare required Reddit scopes by defining a callable
    `get_reddit_scopes` at the MODULE level. This callable must return a list of scopes as strings,
    and must work upon being imported (i.e. without a call to `setup()` or an actual cog/bot
    initialisation).
    """
    _global_config = get_kaztron_config()
    _global_state = get_runtime_config()
    _global_config.set_section_view('reddit', RedditConfig)
    _global_state.set_section_view('reddit', RedditState)
    _config = _global_config.get_section('reddit')  # type: RedditConfig
    _config.set_defaults(refresh_uri='http://localhost:8080')
    _state = _global_state.get_section('reddit')  # type: RedditState
    _state.set_defaults(
        refresh_tokens={},
        last_auth_state=None
    )

    def __init__(self):
        # lazy cache of reddit instance objects
        self.reddit_cache = {u: None for u in self.users}  # type: Dict[str, praw.Reddit]

    @property
    def users(self) -> Sequence[str]:
        return tuple(u for u in self._state.refresh_tokens.keys())

    @property
    def refresh_tokens(self) -> MutableMapping[str, Optional[str]]:
        """ Return a dict of username -> refresh_token """
        return self._state.refresh_tokens

    def get_reddit(self, username: str = None) -> praw.Reddit:
        """
        Get a :class:`praw.Reddit` instance for the specified user.

        :param username: Name of user account to work with. If None, first logged-in user currently
            configured.
        :return: A :class:`praw.Reddit` instance.
        :raise KeyError: User is not currently logged in.
        """
        if username is None:  # if no username specified, set to the first username
            username = self.users[0]
        if username not in self.reddit_cache:
            self.reddit_cache[username] = praw.Reddit(
                client_id=self._config.client_id,
                client_secret=self._config.client_secret,
                refresh_token=self.refresh_tokens[username],
                user_agent=self._config.user_agent
            )
        return self.reddit_cache[username]

    def get_anonymous_reddit(self):
        return praw.Reddit(
            client_id=self._config.client_id,
            client_secret=self._config.client_secret,
            redirect_uri=self._config.refresh_uri,
            user_agent=self._config.user_agent
        )

    def get_extension_scopes(self) -> Set[str]:
        """
        Get reddit scopes required from extensions enabled in the configuration file.

         :raises ImportError: An extension specified in the configuration does not exist.
         """
        import importlib
        scopes = {'identity'}
        for ext_name in self._global_config.get('core', 'extensions'):
            lib = importlib.import_module('kaztron.cog.' + ext_name)
            try:
                ext_scopes = lib.get_reddit_scopes()
                scopes.update(ext_scopes)
                logger.info(f"Extension {ext_name} defines scopes: {ext_scopes!s}")
            except AttributeError:
                logger.warning(f"Extension {ext_name} does not define get_reddit_scopes()")
        return scopes

    def get_authorization_url(self, scopes: Iterable[str] = ('identity',), permanent=True) -> str:
        """
        Get the URL a reddit account owner can use to authorize the bot to log in.

        This will invalidate any previously issued authorisation URLs.

        :param scopes: Reddit API authorisation scopes to request.
        :param permanent: Whether the authorisation should be permanent or temporary (time-limited).
        :return: URL
        """
        with self._state as state:
            state.last_auth_state = secrets.token_urlsafe(16)
        return self.get_anonymous_reddit().auth.url(
            scopes, self._state.last_auth_state, 'permanent' if permanent else 'temporary'
        )

    def authorize(self, state: str, code: str) -> praw.Reddit:
        """
        Once a user has permitted the application, complete the authorization.
        :raise ValueError: State does not match state of last issued authorization URL: the
            authorization may not be one that this application initiated.
        """
        if state != self._state.last_auth_state:
            raise ValueError("State does not match stored state: authorization may not have been "
                             "initiated by this application.")
        reddit = self.get_anonymous_reddit()
        refresh_token = reddit.auth.authorize(code)
        with self._state as state:
            state.refresh_tokens[reddit.user.me().name] = refresh_token
            state.refresh_tokens = self._state.refresh_tokens  # force marking as modified
            self.reddit_cache[reddit.user.me().name] = reddit
        logger.info(f"Authorised user {reddit.user.me().name}")
        return reddit

    def logout(self, username: str):
        """
        Doesn't really logout (not meaningful server-side), but clears stored authorization
        information for that user.
        :raises KeyError: User not logged in.
        """
        del self.reddit_cache[username]
        del self._state.refresh_tokens[username]
        with self._state as state:
            state.refresh_tokens = self._state.refresh_tokens  # force marking as modified
        logger.info(f"Logged out user {username}")

    def clear(self):
        """ Clear all login information for all reddit users. """
        logger.debug("Logging out all known users: {}".format(', '.join(self.users)))
        self.reddit_cache.clear()
        with self._state as state:
            state.refresh_tokens = {}
        logger.info("Logged out all users")

