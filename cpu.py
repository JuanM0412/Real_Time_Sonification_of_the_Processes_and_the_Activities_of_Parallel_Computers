import subprocess
import re
import argparse
import time

# Función para obtener el estado de los nodos desde sinfo
def get_state(nodes):
    nodes_state = {}
    try:
        # Comando para obtener el estado de los nodes
        sinfo_command = "sinfo -o=%t-%n"
        result = subprocess.run(sinfo_command, shell=True, capture_output=True, text=True, check=True)
        
        # Parsear la salida de sinfo
        for line in result.stdout.splitlines():
            # Ignorar la primera línea (encabezado)
            if line.startswith("=STATE-HOSTNAMES"):
                continue
            
            # Separar el estado y el nombre del node
            if "-" in line:
                state, node = line.strip("=").split("-", 1)
                
                # Si el node está en la lista de nodes que nos interesan, guardar su estado
                if node in nodes:
                    nodes_state[node] = state
        
        print('Nodes states:', nodes_state)
            
    except subprocess.CalledProcessError as e:
        print(f"Sinfo exit code: {e}")
    except Exception as e:
        print(f"Unkwon error: {e}")
    
    return nodes_state

# Función para obtener el uso de CPU de un node
def get_cpu_usage(node):
    try:
        ssh_command = f"ssh {node} 'top -b -n1 | grep Cpu'"
        result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True, check=True)
        
        cpu_usages = re.findall(r'(\d+\.\d+) id', result.stdout)
        total_cpu_usage = (100 - sum(map(float, cpu_usages)) / len(cpu_usages)) / 100
        
        return total_cpu_usage
    
    except subprocess.CalledProcessError as e:
        print(f"Error on {node}: {e}")
        return None
    except Exception as e:
        print(f"Unkwon error {node}: {e}")
        return None

# Función principal
def main():
    # Configurar argparse para manejar los argumentos de la línea de comandos
    parser = argparse.ArgumentParser(description="Obtener el uso de CPU de los nodes especificados.")
    parser.add_argument("--nodes", required=True, help="Números de los nodes separados por comas (por ejemplo, 0,30,34)")
    parser.add_argument("--times", type=int, default=1, help="Número de veces (segundos) para verificar el uso de CPU")
    args = parser.parse_args()

    # Generar la lista de nodes
    node_numbers = args.nodes.split(",")
    nodes = [f"compute-0-{num.strip()}" for num in node_numbers]
    
    # Obtener los estados de los nodes
    node_state = get_state(nodes)

    # Abrir el archivo de salida
    with open("cpu_usage_output.txt", "w") as file:
        for step in range(args.times):
            file.write(f"// step = {step}; duration = 1\n[\n")
            
            for node in nodes:
                cpu_usage = get_cpu_usage(node)
                if cpu_usage is not None:
                    print(f'Node -> {node}, Usage -> {cpu_usage}')
                    file.write(f'["cluster" -> {cpu_usage}, "idle" -> {1 - cpu_usage}], // node {node}\n')
                else:
                    file.write(f'["cluster" -> 0.0, "idle" -> 1.0], // node {node} (error)\n')
            
            file.write("],\n")
            
            if step < args.times - 1:
                time.sleep(1)  # Esperar 1 segundo antes del siguiente paso

if __name__ == "__main__":
    main()
