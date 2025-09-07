# News Advisor AI (NA AI)

### The Foundation of Innovation: Making News Reliable

News Advisor AI (NA AI) is an advanced, user-friendly fact-checking system designed to combat the spread of misinformation. In an era where fake news and AI-generated content can easily mislead the public, our solution provides not just a verdict but clear, evidence-backed explanations to verify information.

---

## 🎯 The Problem

In today's digital landscape, fake news and AI-generated images spread rapidly, often appearing highly believable.
This can lead to public panic, the spread of propaganda, and even violence motivated by false information.
Vulnerable groups, such as older individuals and those less exposed to technology, are particularly susceptible.
While the problem is growing with the boom in AI, very few accessible and easy-to-use programs exist to counter it.

---

## ✨ Our Solution

News Advisor AI is our answer to this challenge. It is a user-friendly, chatbot-based AI fact-checking system that:
1.  **Verifies Claims:** Users can submit suspicious news, text, or photos for verification.
2.  **Provides Evidence:** Instead of a simple "true or false" label, NA AI explains *why* a piece of news is misleading and provides factual evidence from credible sources.
3.  **Is Highly Accessible:** Designed for seamless integration into **WhatsApp** and **Telegram**, it brings fact-checking to the platforms where misinformation is most rampant.

---

## 🚀 Key Features

* **Explainable AI**: Delivers clear, human-friendly explanations with links to credible sources, empowering users to understand the facts.
* **Simple & Accessible**: A chatbot-style interface makes it easy for anyone to use, regardless of their technical proficiency.
* **Platform Integration**: Works directly within WhatsApp and Telegram, allowing users to verify information without switching apps.
* **Advanced Technology**: Leverages a state-of-the-art **Retrieval-Augmented Generation (RAG)** architecture with AWS Bedrock and Natural Language Inference (NLI) models like RoBERTa for high accuracy.

---

## 🏗️ System Architecture

Our system is built on a modern, serverless architecture to ensure scalability and reliability.

**Data Flow:**
1.  **Claim Input**: A user submits a claim through the **React** frontend.
2.  **Backend Processing**: The request is sent via **AWS API Gateway** to a **FastAPI** application running on **AWS Lambda**.
3.  **NLP Preprocessing**: The claim is cleaned, and its core proposition is extracted using **Hugging Face Transformers**.
4.  **Evidence Retrieval (RAG)**: The processed claim is sent to **AWS Bedrock Knowledge Base**, which searches curated, trusted fact-checking datasets to find relevant evidence.
5.  **Evidence Classification**: An NLI model (like **RoBERTa-large-MNLI**) compares the claim against the retrieved evidence to classify it as "Supports," "Refutes," or "Uncertain".
6.  **Explanation & Verdict**: The system aggregates the results, assigns a final verdict, and generates a natural language explanation citing the evidence.
7.  **Response**: A JSON object containing the verdict and explanation is returned to the user.


## 🛠️ Tech Stack

Our solution is built using a powerful and modern tech stack:

* **Frontend**: React / Vue.js
* **Backend**: FastAPI, AWS Lambda
* **NLP Models**: Hugging Face Transformers
* **Retrieval & Verification**: AWS Bedrock Knowledge Base, RoBERTa-large-MNLI
* **Storage**: AWS S3, PostgreSQL (for logging)
* **Deployment**: Amazon Web Services (AWS)



## 🔮 Future Scope

We are committed to continuously improving NA AI to build a safer digital world. Our future plans include:
* **Enhanced Media Support**: Adding detection for AI-generated video and audio files.
* **Multi-Language Capabilities**: Expanding our model to support multiple languages.
* **Direct Link Verification**: Allowing users to verify news articles directly from shared links.
* **Continuous Improvement**: Constantly refining the UI/UX and increasing model accuracy.



## 👨‍💻 Meet Our Innovators

This project is brought to you by a dedicated team of innovators:

* **Saksham Pahariya**
* **Mehul Batham**
* **Yathartha Jain**
* **Vasant Kumar Mogia**

### Installation  Guide

- Install Python 3.9+ and a package manager like pip.

- Install Node.js and npm for the React frontend.

- Install the AWS CLI and configure it with your credentials by running aws configure.

- Choose a code editor like VS Code.

- Install Git.

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
