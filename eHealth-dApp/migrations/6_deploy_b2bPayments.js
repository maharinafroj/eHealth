'use strict';

const b2bPayment = artifacts.require('./b2bPayment.sol');

module.exports = function(deployer) {
  deployer.deploy(b2bPayment);
};
