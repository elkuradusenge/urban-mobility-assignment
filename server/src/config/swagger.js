import swaggerJsdoc from "swagger-jsdoc";

const options = {
  definition: {
    openapi: "3.0.0",
    info: {
      title: "Urban Mobility API",
      version: "1.0.0",
      description: "API documentation for the Urban Mobility Assignment",
    },
    servers: [
      {
        url: "http://localhost:3000",
        description: "Local development server",
      },
    ],
  },
  apis: ["./src/docs/*.yaml"],
};

const swaggerSpec = swaggerJsdoc(options);

export default swaggerSpec;
