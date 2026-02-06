const hre = require("hardhat");
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
