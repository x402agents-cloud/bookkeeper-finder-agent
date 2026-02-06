"""
ERC-8004 Identity Registration for ContractorFinder Agent
Registers the agent on Base blockchain with discoverable metadata
"""

import json
import os
from typing import Dict, Optional

# ERC-8004 Identity Registry (Base Mainnet)
# This is a placeholder - actual contract address would be from deployment
ERC8004_REGISTRY = {
    "base_mainnet": "0x...",  # Would be deployed contract address
    "base_sepolia": "0x..."   # Testnet contract
}

class ERC8004Identity:
    """
    ERC-8004 Agent Identity Registration
    
    ERC-8004 defines a standard for agent identity on EVM chains:
    - Agent metadata (name, version, capabilities)
    - Payment configuration (x402)
    - Endpoint URIs
    - Reputation/verification status
    """
    
    def __init__(self, network: str = "base_sepolia"):
        self.network = network
        self.wallet_address = os.getenv("BASE_WALLET_ADDRESS")
        self.api_endpoint = os.getenv("API_ENDPOINT", "https://ca-contractor-finder-production.up.railway.app")
        
    def generate_metadata(self) -> Dict:
        """
        Generate ERC-8004 compliant agent metadata
        """
        return {
            # Required fields (ERC-8004 standard)
            "erc": "8004",
            "version": "1.0.0",
            "name": "ContractorFinder",
            "description": "AI agent that finds licensed contractors with verified reviews",
            "agent_type": "service",
            
            # Identity
            "owner": self.wallet_address,
            "created_at": "2026-02-06T00:00:00Z",
            
            # Capabilities
            "capabilities": [
                "contractor_search",
                "license_verification",
                "review_aggregation"
            ],
            
            # Payment configuration (x402)
            "payment": {
                "protocol": "x402",
                "scheme": "exact",
                "network": "base",
                "asset": "USDC",
                "amount": "0.10",
                "receiver": self.wallet_address,
                "facilitator": "https://facilitator.coinbase.com"
            },
            
            # Endpoints
            "endpoints": {
                "api": self.api_endpoint,
                "health": f"{self.api_endpoint}/health",
                "payment_info": f"{self.api_endpoint}/payment-info",
                "mcp": f"{self.api_endpoint}/mcp"
            },
            
            # Protocols supported
            "protocols": ["http", "mcp", "x402"],
            
            # Metadata
            "metadata": {
                "category": "professional_services",
                "tags": ["contractors", "construction", "licenses", "reviews"],
                "pricing_model": "per_request",
                "documentation": "https://github.com/yourname/contractor-finder-agent",
                "terms_of_service": "https://yourdomain.com/tos",
                "privacy_policy": "https://yourdomain.com/privacy"
            },
            
            # Verification (self-attested for MVP)
            "verification": {
                "status": "self_attested",
                "attestation": None,  # Would be cryptographic signature
                "verified_by": None   # Would be third-party verifier
            }
        }
    
    def generate_solidity_contract(self) -> str:
        """
        Generate ERC-8004 compliant Solidity contract
        """
        contract = '''// SPDX-License-Identifier: MIT
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
'''
        return contract
    
    def generate_deployment_script(self) -> str:
        """
        Generate Hardhat deployment script
        """
        script = '''const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  
  console.log("Deploying ERC-8004 Agent Identity Registry...");
  console.log("Deployer:", deployer.address);
  
  const AgentIdentityRegistry = await hre.ethers.getContractFactory("AgentIdentityRegistry");
  const registry = await AgentIdentityRegistry.deploy();
  
  await registry.waitForDeployment();
  
  const address = await registry.getAddress();
  console.log("ERC-8004 Registry deployed to:", address);
  
  // Save deployment info
  const deploymentInfo = {
    network: hre.network.name,
    contract: "AgentIdentityRegistry",
    address: address,
    deployer: deployer.address,
    timestamp: new Date().toISOString()
  };
  
  require('fs').writeFileSync(
    'erc8004-deployment.json',
    JSON.stringify(deploymentInfo, null, 2)
  );
  
  console.log("Deployment info saved to erc8004-deployment.json");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
'''
        return script
    
    def generate_registration_script(self) -> str:
        """
        Generate script to register agent on deployed contract
        """
        script = '''const hre = require("hardhat");
const fs = require('fs');

async function main() {
  // Load deployment info
  const deployment = JSON.parse(fs.readFileSync('erc8004-deployment.json', 'utf8'));
  
  // Load metadata
  const metadata = JSON.parse(fs.readFileSync('erc8004-metadata.json', 'utf8'));
  
  // Connect to deployed contract
  const AgentIdentityRegistry = await hre.ethers.getContractFactory("AgentIdentityRegistry");
  const registry = AgentIdentityRegistry.attach(deployment.address);
  
  console.log("Registering agent on ERC-8004 registry...");
  console.log("Registry:", deployment.address);
  
  // In production, upload metadata to IPFS and use that URI
  // For MVP, we'll use a data URI or HTTPS endpoint
  const metadataURI = "https://yourdomain.com/erc8004-metadata.json";
  
  const tx = await registry.register(metadataURI);
  await tx.wait();
  
  console.log("✅ Agent registered successfully!");
  console.log("Transaction:", tx.hash);
  
  // Verify registration
  const identity = await registry.getIdentity(await registry.signer.getAddress());
  console.log("Identity:", identity);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
'''
        return script
    
    def save_metadata(self, output_path: str = "erc8004-metadata.json"):
        """Save metadata to JSON file"""
        metadata = self.generate_metadata()
        with open(output_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✅ ERC-8004 metadata saved to {output_path}")
        return output_path
    
    def save_contract(self, output_path: str = "contracts/ERC8004Registry.sol"):
        """Save Solidity contract to file"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        contract = self.generate_solidity_contract()
        with open(output_path, 'w') as f:
            f.write(contract)
        print(f"✅ Solidity contract saved to {output_path}")
        return output_path
    
    def print_summary(self):
        """Print summary of ERC-8004 integration"""
        print("="*60)
        print("ERC-8004 AGENT IDENTITY REGISTRATION")
        print("="*60)
        print("\n📋 What is ERC-8004?")
        print("Standard for AI agent identity on EVM chains")
        print("Enables discoverability, reputation, and interoperability")
        print("\n🔧 Components Generated:")
        print("  1. Agent Metadata (JSON)")
        print("  2. Identity Registry Contract (Solidity)")
        print("  3. Deployment Scripts (Hardhat)")
        print("\n📄 Files Created:")
        print("  - erc8004-metadata.json")
        print("  - contracts/ERC8004Registry.sol")
        print("  - scripts/deploy-erc8004.js")
        print("  - scripts/register-agent.js")
        print("\n⛓️ Deployment Steps:")
        print("  1. Deploy registry contract to Base")
        print("  2. Upload metadata to IPFS")
        print("  3. Register agent on contract")
        print("  4. Verify on BaseScan")
        print("\n💡 Benefits:")
        print("  - Agents are discoverable on-chain")
        print("  - Reputation can be tracked publicly")
        print("  - Standard for agent marketplaces")
        print("  - Interoperable across platforms")
        print("="*60)

def main():
    """Generate all ERC-8004 files"""
    erc8004 = ERC8004Identity(network="base_mainnet")
    
    # Save metadata
    erc8004.save_metadata("erc8004-metadata.json")
    
    # Save contract
    erc8004.save_contract("contracts/ERC8004Registry.sol")
    
    # Save deployment script
    with open("scripts/deploy-erc8004.js", 'w') as f:
        f.write(erc8004.generate_deployment_script())
    print("✅ Deployment script saved to scripts/deploy-erc8004.js")
    
    # Save registration script
    with open("scripts/register-agent.js", 'w') as f:
        f.write(erc8004.generate_registration_script())
    print("✅ Registration script saved to scripts/register-agent.js")
    
    # Print summary
    print()
    erc8004.print_summary()

if __name__ == "__main__":
    main()
