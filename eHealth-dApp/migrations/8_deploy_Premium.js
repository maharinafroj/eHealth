'use strict';

const premium = artifacts.require('./Premium.sol');

module.exports = function(deployer) {
  deployer.deploy(premium);
};
