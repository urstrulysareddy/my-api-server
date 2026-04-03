const express = require("express");
const serverless = require("serverless-http");
const { PrismaClient } = require("@prisma/client");

const app = express();
const prisma = new PrismaClient();

app.use(express.json());

// Example route
app.get("/api/hello", (req, res) => {
  res.json({ message: "Hello World!" });
});

// Export as serverless handler
module.exports = app;
module.exports.handler = serverless(app);