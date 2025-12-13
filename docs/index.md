# Welcome to the Homelab

This is the documentation for our home infrastructure - a collection of servers that provide various services for the household.

## What is a Homelab?

A homelab is a personal computing environment, typically consisting of servers and networking equipment, used for learning, experimentation, and running self-hosted services. Instead of relying on cloud providers like Google or Amazon, we run our own versions of common services.

## What Does This Homelab Do?

### AI & Machine Learning
We run our own AI models locally. This means we can use ChatGPT-like assistants without sending data to external companies. The AI runs on dedicated graphics cards (GPUs) for fast responses.

### Media & Entertainment
Movies, TV shows, and music are stored and streamed throughout the house. Think of it like a personal Netflix that you control.

### Backups & Storage
Important files, photos, and documents are automatically backed up. If a computer fails, nothing is lost.

### Home Automation
Smart home devices, sensors, and automation rules run locally - no cloud dependency, no privacy concerns.

### Development Tools
Code repositories, continuous integration, and development environments for software projects.

## How is it Built?

The homelab uses **Proxmox**, a system that lets one physical server run many virtual servers. This is more efficient than having separate physical machines for each service.

Everything is configured using **Ansible**, which is automation software. Instead of manually setting up each server, we describe what we want in code, and Ansible makes it happen. This means:

- **Reproducible**: If something breaks, we can rebuild it exactly as it was
- **Documented**: The code itself documents how everything is configured
- **Version controlled**: We can track every change and roll back if needed

## Quick Links

- [Architecture Overview](architecture/overview.md) - See how everything connects
- [Hosts](architecture/hosts.md) - Learn about each server
- [Services](architecture/services.md) - What services are available

## Network Access

All services are available on the local network. If you're connected to the home WiFi or ethernet, you can access everything listed in the [Services](architecture/services.md) page.
