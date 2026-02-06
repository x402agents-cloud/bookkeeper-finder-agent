// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title ERC8004 Agent Identity
 * @notice Identity registry for AI agents on Base
 * @dev Implements ERC-8004 standard for agent discoverability
 */

contract AgentIdentityRegistry {
    
    struct AgentIdentity {
        address owner;
        string metadataURI;
        uint256 registeredAt;
        bool isActive;
        uint256 reputationScore;
    }
    
    // agent address => identity
    mapping(address => AgentIdentity) public identities;
    
    // owner => list of agents
    mapping(address => address[]) public ownerAgents;
    
    // All registered agents
    address[] public allAgents;
    
    event AgentRegistered(
        address indexed agent,
        address indexed owner,
        string metadataURI,
        uint256 registeredAt
    );
    
    event AgentUpdated(
        address indexed agent,
        string newMetadataURI,
        uint256 updatedAt
    );
    
    event AgentDeactivated(address indexed agent, uint256 deactivatedAt);
    
    modifier onlyOwner(address agent) {
        require(identities[agent].owner == msg.sender, "Not agent owner");
        _;
    }
    
    /**
     * @notice Register a new agent identity
     * @param metadataURI IPFS or HTTPS URI to ERC-8004 metadata JSON
     */
    function register(string calldata metadataURI) external {
        require(bytes(metadataURI).length > 0, "Metadata URI required");
        require(identities[msg.sender].registeredAt == 0, "Agent already registered");
        
        identities[msg.sender] = AgentIdentity({
            owner: msg.sender,
            metadataURI: metadataURI,
            registeredAt: block.timestamp,
            isActive: true,
            reputationScore: 0
        });
        
        ownerAgents[msg.sender].push(msg.sender);
        allAgents.push(msg.sender);
        
        emit AgentRegistered(
            msg.sender,
            msg.sender,
            metadataURI,
            block.timestamp
        );
    }
    
    /**
     * @notice Update agent metadata
     */
    function updateMetadata(string calldata newMetadataURI) external {
        require(identities[msg.sender].isActive, "Agent not active");
        identities[msg.sender].metadataURI = newMetadataURI;
        
        emit AgentUpdated(msg.sender, newMetadataURI, block.timestamp);
    }
    
    /**
     * @notice Deactivate agent
     */
    function deactivate() external {
        identities[msg.sender].isActive = false;
        emit AgentDeactivated(msg.sender, block.timestamp);
    }
    
    /**
     * @notice Get agent identity
     */
    function getIdentity(address agent) external view returns (AgentIdentity memory) {
        return identities[agent];
    }
    
    /**
     * @notice Get all agents count
     */
    function getAgentCount() external view returns (uint256) {
        return allAgents.length;
    }
    
    /**
     * @notice Check if address is registered agent
     */
    function isRegistered(address agent) external view returns (bool) {
        return identities[agent].registeredAt > 0;
    }
}
