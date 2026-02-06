const hre = require("hardhat");

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
