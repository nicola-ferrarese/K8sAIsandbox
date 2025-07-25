
# JupyterHub, MinIO, ~~MLFlow, Kserve & Keycloak~~ on Kubernetes
A complete deployment setup for running JupyterHub on Kubernetes with PostgreSQL backend, MetalLB load balancing, and NGINX ingress controller. 

This configuration supports both local development with Minikube and production bare-metal deployments.

## 🏗️ Architecture

This setup includes:
- **JupyterHub**: Multi-user Jupyter notebook server
- **MinIO**: Object and artifact storage
- **PostgreSQL**: Persistent database backend for JupyterHub
- **NGINX Ingress Controller**: HTTP/HTTPS routing and load balancing
- **MetalLB**: Load balancer implementation for bare-metal Kubernetes clusters

## 📁 Repository Structure

```
├── configs/
│   ├── minio-values               # MinIo configuration
│   ├── postgresql-values.yaml     # PostgreSQL configuration
│   └── jupyter-values.yaml        # JupyterHub configuration
├── Metallb-helm-config/
│   ├── metallb-config.yaml        # MetalLB IP pool configuration
│   └── values.yaml                # MetalLB Helm values
└── README.md                      # This file
```

## 🚀 Quick Start

### Prerequisites

- Kubernetes cluster (Minikube for local development)
- Helm 3.x
- kubectl configured to access your cluster

## 📦 Installation Steps

### 1. Add Helm Repositories

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/
helm repo add metallb https://metallb.github.io/metallb
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add minio https://charts.min.io/
helm repo update
```

### 2. Install NGINX Ingress Controller

```bash
# Download chart for reference (optional)
helm pull ingress-nginx/ingress-nginx --untar

# Install NGINX Ingress
helm install ingress-nginx ingress-nginx/ingress-nginx
```

### 3. Setup MetalLB

```bash
# Create MetalLB namespace
kubectl create namespace metallb-system

# Install MetalLB
helm install metallb metallb/metallb \
  --namespace metallb-system \
  -f Metallb-helm-config/values.yaml

# Configure IP address pool
kubectl apply -f Metallb-helm-config/metallb-config.yaml
```

### 4. Install PostgreSQL

```bash
# Install PostgreSQL in jupyter namespace
helm install postgresql bitnami/postgresql \
  --namespace jupyter \
  --create-namespace \
  -f jupyterhub-helm-config/postgresql-values.yaml
```

### 5. Install JupyterHub

```bash
# Download chart for reference (optional)
helm pull jupyterhub/jupyterhub --untar

# Install JupyterHub
helm upgrade --install jupyter jupyterhub/jupyterhub \
  --namespace jupyter \
  --create-namespace \
  -f config/jupyter-values.yaml
```
### 6. Install MinIO
```
helm install minio minio/minio \
  -n minio --create-namespace \
  -f config/minio-values.yaml
```

## 🔧 Configuration

### JupyterHub Configuration

The `jupyterhub-helm-config/values.yaml` file contains:
- PostgreSQL database connection
- Ingress configuration for `jupyter.local`
- Security contexts optimized for Minikube
- Single-user notebook configuration

### PostgreSQL Configuration

The `jupyterhub-helm-config/postgresql-values.yaml` includes:
- Minikube-specific permission fixes
- Volume permissions configuration
- Database initialization scripts

### MetalLB Configuration

The `Metallb-helm-config/` directory contains:
- IP address pool configuration
- LoadBalancer service settings

## 🌐 Access

### Local Development (Minikube)

1. Add to your `/etc/hosts` file:
   ```
   <Your cluster IP> jupyter.local minio.local minio-console.local
   ```

2. Access JupyterHub at: `http://jupyter.local`
3. Access to MinIo at: `http://minio-console.local`


### Useful Commands

```bash
# View JupyterHub logs
kubectl logs -f deployment/hub -n jupyter

# View PostgreSQL logs
kubectl logs -f postgresql-0 -n jupyter

# Restart JupyterHub
kubectl rollout restart deployment/hub -n jupyter

# Test PostgreSQL connection
kubectl run postgresql-client --rm --tty -i --restart='Never' \
  --namespace jupyter \
  --image docker.io/bitnami/postgresql:15 \
  --env="PGPASSWORD=yourpassword" \
  --command -- psql --host postgresql --port 5432 -U postgres -d jupyterhub
```

## 🔄 Upgrades

To upgrade JupyterHub:

```bash
helm repo update
helm upgrade jupyter jupyterhub/jupyterhub \
  --namespace jupyter \
  -f jupyterhub-helm-config/values.yaml
```

To upgrade PostgreSQL:

```bash
helm upgrade postgresql bitnami/postgresql \
  --namespace jupyter \
  -f jupyterhub-helm-config/postgresql-values.yaml
```

## 🔗 References

- [JupyterHub Documentation](https://jupyterhub.readthedocs.io/)
- [JupyterHub Helm Chart](https://jupyterhub.github.io/helm-chart/)
- [PostgreSQL Bitnami Chart](https://github.com/bitnami/charts/tree/main/bitnami/postgresql)
- [MetalLB Documentation](https://metallb.universe.tf/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
