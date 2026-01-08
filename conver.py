import json
import os
import argparse

def convert_json_to_target(input_file_path, output_file_path="./target.txt"):
    ip_port_set = set()
    
    try:
        with open(input_file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    ip = data.get('ip')
                    port = data.get('port')
                    
                    if ip and port:
                        ip_port = f"{ip}:{port}"
                        ip_port_set.add(ip_port)
                    else:
                        print(f"[Warning] Line {line_num}: Missing ip or port field, skipped: {line}")
                        
                except json.JSONDecodeError:
                    print(f"[Error] Line {line_num}: Invalid JSON format, skipped: {line}")
                except Exception as e:
                    print(f"[Error] Line {line_num}: Processing failed: {str(e)}, content: {line}")
        
        with open(output_file_path, 'w', encoding='utf-8') as f:
            sorted_ip_ports = sorted(ip_port_set)
            for ip_port in sorted_ip_ports:
                f.write(f"{ip_port}\n")
        
        print(f"[Success] Converted {len(sorted_ip_ports)} unique ip:port entries, saved to {output_file_path}")
        
    except FileNotFoundError:
        print(f"[Error] Input file {input_file_path} not found, please check the path!")
    except PermissionError:
        print(f"[Error] Permission denied to read/write files, please check file permissions!")
    except Exception as e:
        print(f"[Error] Program execution failed: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Convert ip:port data in line-separated JSON format to plain ip:port text format')
    parser.add_argument('-i', '--input', 
                        required=True, 
                        help='Path to input JSON file (required, e.g.: ./input.json)')
    parser.add_argument('-o', '--output', 
                        default="./target.txt", 
                        help='Path to output target file (optional, default: ./target.txt)')
    
    args = parser.parse_args()
    convert_json_to_target(args.input, args.output)

if __name__ == "__main__":
    main()