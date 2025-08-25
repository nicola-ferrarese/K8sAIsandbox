
## Quick Self-Signed Cert

1. **Install cert-manager**:

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml
```

2. **Create a ClusterIssuer** for self-signed certs:

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: selfsigned-issuer
spec:
  selfSigned: {}
```

```bash
kubectl apply -f selfsigned-issuer.yaml
```

3. **Create a Certificate** for the domains:

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: clearml-tls
  namespace: default
spec:
  secretName: clearml-tls
  commonName: clearml.local
  dnsNames:
  - app.clearml.local
  - api.clearml.local
  - files.clearml.local
  issuerRef:
    name: selfsigned-issuer
    kind: ClusterIssuer
```

```bash
kubectl apply -f clearml-tls.yaml
```

4. **Update your Ingresses** to use TLS