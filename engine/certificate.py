#!/usr/bin/env python3
"""
World Completion Certificate Generator
Generates achievement certificates for completing K8sQuest worlds
"""

import sys
from datetime import datetime
from pathlib import Path

def generate_certificate(world_num, player_name, total_xp):
    """Generate a completion certificate for a world"""
    
    world_info = {
        1: {
            "name": "Core Kubernetes Basics",
            "levels": 10,
            "skills": [
                "Debug CrashLoopBackOff errors",
                "Fix ImagePullBackOff issues",
                "Resolve Pending pod problems",
                "Work with label selectors",
                "Debug port mismatches",
                "Manage multi-container pods",
                "Navigate container logs",
                "Understand init containers",
                "Work with namespaces",
                "Handle resource quotas"
            ]
        },
        2: {
            "name": "Deployments & Scaling",
            "levels": 10,
            "skills": [
                "Rollback failed deployments",
                "Configure liveness probes",
                "Configure readiness probes",
                "Set up HorizontalPodAutoscaler",
                "Optimize rollout strategies",
                "Work with PodDisruptionBudgets",
                "Implement blue-green deployments",
                "Implement canary deployments",
                "Choose StatefulSet vs Deployment",
                "Understand ReplicaSet management"
            ]
        }
    }
    
    if world_num not in world_info:
        print(f"❌ World {world_num} not found")
        return
    
    world = world_info[world_num]
    date = datetime.now().strftime("%B %d, %Y")
    
    certificate = f"""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║              🏆 WORLD {world_num} COMPLETE! 🏆                      ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

Player: {player_name}
World: {world_info[world_num]['name']}
Date: {date}

📊 Achievement:
   • {world['levels']} Levels Completed
   • {total_xp} XP Earned

🎯 Skills Mastered:
"""
    
    for i, skill in enumerate(world['skills'], 1):
        certificate += f"   {i:2d}. {skill}\n"
    
    certificate += "\n"
    
    if world_num == 1:
        certificate += "Next: World 2 - Deployments & Scaling\n"
    elif world_num == 2:
        certificate += "Next: World 3 - Networking & Services\n"
    
    certificate += """
🎮 Keep learning, keep fixing Kubernetes! 🎮

"""
    
    return certificate


def save_certificate(world_num, certificate):
    """Save certificate to file"""
    cert_dir = Path(__file__).parent.parent / "certificates"
    cert_dir.mkdir(exist_ok=True)
    
    cert_file = cert_dir / f"world-{world_num}-completion.txt"
    
    with open(cert_file, 'w', encoding='utf-8') as f:
        f.write(certificate)
    
    return cert_file


def main():
    if len(sys.argv) < 4:
        print("Usage: python3 certificate.py <world_num> <player_name> <total_xp>")
        print("Example: python3 certificate.py 1 'Jane Doe' 1450")
        sys.exit(1)
    
    world_num = int(sys.argv[1])
    player_name = sys.argv[2]
    total_xp = int(sys.argv[3])
    
    certificate = generate_certificate(world_num, player_name, total_xp)
    
    if certificate:
        # Print to console
        print(certificate)
        
        # Save to file
        cert_file = save_certificate(world_num, certificate)
        print(f"✅ Certificate saved to: {cert_file}")
        print("")
        print("🎉 Congratulations on completing this world!")


if __name__ == "__main__":
    main()
