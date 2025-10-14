# NETwork
![alt text](https://github.com/homodudu/Machine-Learning/blob/main/NETwork/_documentation/NETwork%20Welcome%20Poster.png)

## Overview
NETwork is a multi-agent chat application delivering tennis instruction, forecasts, betting insights, and strategic recommendations.

### Process Flow
NETwork utilises the Microsoft Azure framework to deliver a dynamic web applicatiion.

![alt text](https://github.com/homodudu/Machine-Learning/blob/main/NETwork/_documentation/Process%20Flow.png)

### Multi-Agent Solution
The orchestrated workflow consist of three connected Chat-GPT models, each with a content delivery role. 

![alt text](https://github.com/homodudu/Machine-Learning/blob/main/NETwork/_documentation/Multi-Agent%20Solution.png)

## Backend
The backend for the NETwork app is written in Python, managing interactions with Azure resources via the Azure SDK API. The python code implements a FastAPI server to interact with the React frontend. It is deployed on Azure as a web app. 

### AI Foundry

![alt text](https://github.com/homodudu/Machine-Learning/blob/main/NETwork/_documentation/Foundry%20Portal.png)

The backend serves as an intermediary between the frontend UI and Azure Foundry, relaying user messages to the "Connect" Foundry agent and delivering the agent’s orchestrated response back to the frontend.

### Statistical Data
The backend statistical data is retrieved from the following resource:
https://github.com/JeffSackmann (Licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.)

## Frontend
The frontend for the NETwork app is built using React, managing client-side interactions with the FastAPI server implemented in the Python backend. It is deployed on Azure as a static web app.

![alt text](https://github.com/homodudu/Machine-Learning/blob/main/NETwork/_documentation/NETwork%20Frontend%20React.png)

### Template
The frontend is developed using a customized version of the Google Gemini-style application template from codingnepalweb.com

https://buymeacoffee.com/codingnepal/e/402506 (Licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.)

## Author
[@homodudu](https://github.com/homodudu)
