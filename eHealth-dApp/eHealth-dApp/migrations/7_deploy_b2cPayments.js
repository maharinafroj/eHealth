'use strict';

const b2cPayment = artifacts.require('./b2cPayment.sol');

module.exports = function(deployer) {
  deployer.deploy(b2cPayment);
};
