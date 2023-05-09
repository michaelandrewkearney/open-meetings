module.exports = async function () {
  const shell = require("shelljs")
  console.log("tearing down server")
  shell.exec("docker stop opm")
};