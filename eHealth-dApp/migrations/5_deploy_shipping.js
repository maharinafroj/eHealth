'use strict';

const shipping = artifacts.require('./shipping.sol');

module.exports = function(deployer) {
  deployer.deploy(shipping);
};
