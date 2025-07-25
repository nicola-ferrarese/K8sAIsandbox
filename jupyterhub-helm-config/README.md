# JupyterHub Helm Configuration

This project contains the configuration settings for deploying JupyterHub using Helm. The configuration is specified in the `values.yaml` file, which includes various settings to customize the JupyterHub deployment.

## Configuration Settings

The `values.yaml` file includes the following key settings:

- **Singleuser Image**:
  - `singleuser.image.name`: Set to `jupyter/base-notebook`.
  - `singleuser.image.tag`: Set to `latest`.

- **Proxy Settings**:
  - `proxy.service.type`: Set to `ClusterIP`.
  - `proxy.https.enabled`: Set to `false`.

- **Singleuser Storage**:
  - `singleuser.storage.capacity`: Set to `5Gi`.

## Usage

To launch JupyterHub using Helm with the provided configuration, run the following command:

```
helm upgrade --install jupyter jupyterhub/jupyterhub \
  --namespace jupyter --create-namespace \
  -f values.yaml
```

This command will install or upgrade the JupyterHub release in the specified namespace using the settings defined in `values.yaml`.