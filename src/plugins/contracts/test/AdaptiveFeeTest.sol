// SPDX-License-Identifier: UNLICENSED
pragma solidity =0.8.20;

import '../base/AlgebraFeeConfiguration.sol';
import '../libraries/AdaptiveFee.sol';

import '@cryptoalgebra/core/contracts/libraries/Constants.sol';

contract AdaptiveFeeTest {
  AlgebraFeeConfiguration public feeConfig;

  constructor() {
    feeConfig = AdaptiveFee.initialFeeConfiguration();
  }

  function getFee(uint88 volatility) external view returns (uint256 fee) {
    return AdaptiveFee.getFee(volatility, AlgebraFeeConfigurationLibrary.pack(feeConfig));
  }

  function getGasCostOfGetFee(uint88 volatility) external view returns (uint256) {
    AlgebraFeeConfigurationPacked _packed = AlgebraFeeConfigurationLibrary.pack(feeConfig);
    unchecked {
      uint256 gasBefore = gasleft();
      AdaptiveFee.getFee(volatility, _packed);
      return gasBefore - gasleft();
    }
  }

  function packAndUnpackFeeConfig(AlgebraFeeConfiguration calldata config) external pure returns (AlgebraFeeConfiguration memory unpacked) {
    AlgebraFeeConfigurationPacked _packed = AlgebraFeeConfigurationLibrary.pack(config);
    unpacked.alpha1 = _packed.alpha1();
    unpacked.alpha2 = _packed.alpha2();
    unpacked.beta1 = _packed.beta1();
    unpacked.beta2 = _packed.beta2();
    unpacked.gamma1 = _packed.gamma1();
    unpacked.gamma2 = _packed.gamma2();
    unpacked.baseFee = _packed.baseFee();
  }
}
