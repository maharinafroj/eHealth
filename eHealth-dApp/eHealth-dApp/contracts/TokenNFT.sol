pragma solidity 0.8.0;

import "https://github.com/0xcert/ethereum-erc721/src/contracts/tokens/nf-token-metadata.sol";
import "https://github.com/0xcert/ethereum-erc721/src/contracts/ownership/ownable.sol";

contract TokenNFT is NFTokenMetadata, Ownable {

constructor() {
nftName = "gfg NFT";
nftSymbol = "GFG";
}

function mint(address _to, uint256 _tokenId, string calldata _uri) external onlyOwner {
super._mint(_to, _tokenId);
super._setTokenUri(_tokenId, _uri);
}

}

