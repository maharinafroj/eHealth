pragma solidity ^0.4.24;
import "github.com/OpenZeppelin/openzeppelin-solidity/contracts/math/SafeMath.sol";

contract B2CPayment {    
    using SafeMath for uint;    
    mapping (address => uint) public deposits;
    
    function getBalance(address _user) public constant returns (uint) {
        return deposits[_user];
    }
    
    function deposit() public payable {
        deposits[msg.sender] = deposits[msg.sender].add(msg.value);
    }
    
    function withdraw(uint _value) public {
        deposits[msg.sender] = deposits[msg.sender].sub(_value);
        msg.sender.transfer(_value);
    }    
}
