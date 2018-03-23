import pytest

from kaztron.driver.stats import MeanVarianceAccumulator


def test_mean_variance():
    data = [1.1020e+2, 1.1010e+2, 1.0670e+2, 9.0840e+1, 9.8650e+1, 1.0530e+2, 9.0480e+1, 8.6950e+1,
            1.0270e+2, 1.0640e+2, 9.2670e+1, 9.8330e+1, 9.4980e+1, 9.4500e+1, 9.1370e+1, 1.1210e+2,
            9.5600e+1, 9.2630e+1, 9.5150e+1, 1.0930e+2, 9.7750e+1, 1.0470e+2, 9.1580e+1, 1.0160e+2,
            9.4550e+1, 1.0230e+2, 1.0510e+2, 1.0470e+2, 1.2100e+2, 8.7820e+1, 9.3190e+1, 1.0960e+2,
            9.6620e+1, 9.9940e+1, 1.0480e+2, 1.0420e+2, 9.9730e+1, 1.0950e+2, 9.3230e+1, 1.0440e+2,
            1.0410e+2, 1.1490e+2, 9.2650e+1, 1.0840e+2, 9.6980e+1, 9.6290e+1, 9.7510e+1, 9.9330e+1,
            8.9810e+1, 1.0240e+2, 1.1000e+2, 8.6630e+1, 1.0130e+2, 9.6970e+1, 1.1130e+2, 9.2160e+1,
            1.1580e+2, 1.1550e+2, 9.2200e+1, 9.5600e+1, 1.0680e+2, 9.4240e+1, 1.0330e+2, 9.9410e+1,
            1.0890e+2, 8.2760e+1, 1.0310e+2, 1.0390e+2, 9.7090e+1, 1.1270e+2, 1.0100e+2, 8.8740e+1,
            1.0530e+2, 9.4330e+1, 1.0610e+2, 9.5890e+1, 1.1310e+2, 1.0350e+2, 8.7660e+1, 9.6140e+1,
            9.6490e+1, 1.0150e+2, 1.1400e+2, 9.6350e+1, 1.0690e+2, 1.0090e+2, 9.7320e+1, 9.3230e+1,
            1.1110e+2, 1.0190e+2, 9.6030e+1, 1.0280e+2, 9.2520e+1, 8.8220e+1, 9.3600e+1, 9.3430e+1,
            1.1150e+2, 1.1670e+2, 1.0040e+2, 9.3160e+1, 1.1220e+2, 8.8830e+1, 1.0580e+2, 1.2990e+2,
            1.0140e+2, 8.6820e+1, 9.2390e+1, 9.4390e+1, 1.1070e+2, 1.0800e+2, 8.9730e+1, 9.0220e+1,
            1.0030e+2, 8.7540e+1, 1.0120e+2, 1.0510e+2, 1.1120e+2, 8.7440e+1, 1.0870e+2, 1.0340e+2,
            1.1160e+2, 1.1390e+2, 9.4290e+1, 1.0620e+2, 1.0080e+2, 8.7150e+1, 1.1050e+2, 1.2910e+2,
            1.0880e+2, 8.7520e+1, 1.0470e+2, 1.1740e+2, 9.3340e+1, 9.2470e+1, 9.4030e+1, 1.0620e+2,
            1.0200e+2, 1.1320e+2, 9.0110e+1, 1.0040e+2, 1.0230e+2, 1.0460e+2, 9.8900e+1, 1.0480e+2,
            7.7510e+1, 1.0590e+2, 9.5450e+1, 9.1810e+1, 9.0570e+1, 1.0350e+2, 1.0510e+2, 1.1150e+2,
            9.1390e+1, 9.3230e+1, 9.1930e+1, 8.9830e+1, 8.7320e+1, 9.7800e+1, 1.0760e+2, 9.6950e+1,
            1.0250e+2, 1.0160e+2, 9.1720e+1, 9.1700e+1, 7.5180e+1, 1.0220e+2, 9.5720e+1, 1.0070e+2,
            1.0330e+2, 1.0100e+2, 9.3290e+1, 1.1310e+2, 1.0050e+2, 1.0230e+2, 9.9960e+1, 1.1360e+2,
            1.0260e+2, 1.0010e+2, 9.5060e+1, 1.0360e+2, 1.0120e+2, 1.2160e+2, 1.0900e+2, 9.6260e+1,
            1.1120e+2, 9.0780e+1, 1.0550e+2, 9.5140e+1, 1.0180e+2, 9.1700e+1, 9.9240e+1, 1.0140e+2,
            1.0800e+2, 1.1250e+2, 1.0090e+2, 8.1120e+1, 9.2090e+1, 1.0230e+2, 9.5640e+1, 8.4730e+1,
            8.2790e+1, 9.1330e+1, 1.0620e+2, 9.2860e+1, 9.1190e+1, 1.1270e+2, 1.0380e+2, 9.3440e+1,
            9.6900e+1, 9.8700e+1, 1.0820e+2, 1.1180e+2, 9.7340e+1, 1.0120e+2, 9.8330e+1, 1.0590e+2,
            1.0910e+2, 1.0490e+2, 9.3940e+1, 9.2630e+1, 1.0770e+2, 1.1880e+2, 1.0040e+2, 8.6340e+1,
            9.0190e+1, 1.0120e+2, 1.2110e+2, 1.0290e+2, 9.7640e+1, 1.0940e+2, 8.1340e+1, 8.7000e+1,
            8.8660e+1, 9.9680e+1, 8.4490e+1, 9.6710e+1, 9.4050e+1, 9.5150e+1, 1.0190e+2, 1.1850e+2,
            9.4090e+1, 1.1420e+2, 1.0410e+2, 1.0300e+2, 1.1290e+2, 9.8640e+1, 9.7700e+1, 1.0130e+2,
            9.6680e+1, 1.0240e+2]
    mean = 100.2532
    stdev = 8.95576
    tol = 0.0001
    dut = MeanVarianceAccumulator()
    for datum in data:
        dut.update(datum)
    assert dut.count == len(data)
    assert dut.sum == sum(data)
    assert dut.mean == pytest.approx(mean, tol)
    assert dut.std_dev == pytest.approx(stdev, tol)


def test_dump():
    data = [3.2550e+1, 5.4380e+1, 2.8120e+1, 4.9680e+1, 4.7800e+1,
            3.6850e+1, 4.6760e+1, 5.2020e+1, 4.0370e+1, 4.1010e+1]
    dut = MeanVarianceAccumulator()
    for datum in data:
        dut.update(datum)
    dut2 = MeanVarianceAccumulator.from_state(*dut.dump_state())
    assert dut2.mean == dut.mean
    assert dut2.std_dev == dut.std_dev
