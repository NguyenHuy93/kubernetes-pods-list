from kubernetes import config , client
from flask import Flask, render_template
import os

app = Flask(__name__)

def get_kube_config():
    try:
        config.load_incluster_config()
    except config.ConfigException:
        try:
            config.load_kube_config()
        except config.ConfigException:
            raise Exception("Could not configure kubernetes python client")
    v1 = client.CoreV1Api()
    return v1

def get_current_namespace():
    ns_path = "/var/run/secrets/kubernetes.io/serviceaccount/namespace"
    if os.path.exists(ns_path):
        with open(ns_path) as f:
            return f.read().strip()
    try:
        _, active_context = config.list_kube_config_contexts()
        return active_context["context"]["namespace"]
    except KeyError:
        return "default"
    
def main():
    v1 = get_kube_config()
    current_ns = get_current_namespace()
    pods = v1.list_namespaced_pod(current_ns)
    pods_details_list = []
    for pod in pods.items:
        dict = {
            "name": pod.metadata.name,
            "namespace": pod.metadata.namespace,
            "ip": pod.status.pod_ip,
            "node": pod.spec.node_name
        }
        pods_details_list.append(dict)
    return (pods_details_list)


@app.route('/')
def hello_world():
    return render_template('index.html', pods_list=main())

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
