#!/bin/bash

echo "Recording demo video..."
echo "Make sure Docker services are running!"

cd frontend
npm install
npm run cypress:run

echo ""
echo "Demo videos created in:"
echo "  frontend/cypress/videos/"
echo ""
echo "The payroll.cy.ts video shows the complete flow!"