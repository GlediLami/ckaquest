#!/usr/bin/env python3
"""
Player name generator for K8sQuest
Generates cool DevOps/SRE themed usernames
"""

import random

ADJECTIVES = [
    "Swift", "Clever", "Bold", "Wise", "Brave", "Sharp", "Quick", "Stellar",
    "Cloud", "Quantum", "Digital", "Cyber", "Ninja", "Master", "Elite", "Pro",
    "Turbo", "Super", "Mega", "Ultra", "Alpha", "Beta", "Prime", "Core",
    "Peak", "Apex", "Vertex", "Summit", "Zenith", "Phoenix"
]

NOUNS = [
    "DevOps", "SRE", "Engineer", "Ops", "Admin", "Architect", "Wizard", "Guru",
    "Ninja", "Samurai", "Knight", "Guardian", "Sentinel", "Warden", "Keeper",
    "Deployer", "Debugger", "Builder", "Coder", "Hacker", "Crafter", "Maker",
    "Cluster", "Pod", "Node", "Helm", "Kubectl", "Docker", "Kube", "Operator"
]

def generate_random_name():
    """Generate a random cool DevOps name"""
    adjective = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    number = random.randint(1, 99)
    
    # Randomly choose format
    formats = [
        f"{adjective}{noun}",
        f"{adjective}{noun}{number}",
        f"{noun}{adjective}",
        f"{adjective}-{noun}",
    ]
    
    return random.choice(formats)

def get_player_name(console, current_name=None):
    """Get player name - either ask user or generate random"""
    from rich.prompt import Prompt, Confirm
    
    if current_name and current_name != "Padawan":
        # Already have a name
        if Confirm.ask(f"Continue as [cyan]{current_name}[/cyan]?", default=True):
            return current_name
    
    # Offer choices
    console.print("\n[yellow]📝 Choose Your Identity:[/yellow]\n")
    console.print("  1. Enter a custom name")
    console.print("  2. Generate a random cool name")
    console.print("  3. Stay as 'Padawan' (default)")
    console.print()
    
    choice = Prompt.ask("Your choice", choices=["1", "2", "3"], default="2")
    
    if choice == "1":
        name = Prompt.ask("Enter your name", default="K8s Explorer")
        return name.strip()
    elif choice == "2":
        generated = generate_random_name()
        console.print(f"\n[green]✨ Generated name: [bold]{generated}[/bold][/green]")
        if Confirm.ask("Use this name?", default=True):
            return generated
        else:
            # Try again or enter custom
            return get_player_name(console, current_name)
    else:
        return "Padawan"

if __name__ == "__main__":
    # Test the generator
    print("Sample random names:")
    for _ in range(10):
        print(f"  • {generate_random_name()}")
