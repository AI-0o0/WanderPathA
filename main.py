from __future__ import annotations

from typing import Callable


def run_reactive() -> None:
    from reactive.agent import run_agent

    run_agent()


def run_unconstrained() -> None:
    from unconstrained_react.agent import run_agent

    run_agent()


def run_routing() -> None:
    print("\nRouting Agent")
    print("This project does not contain a full routing agent yet.")
    print("Enter a short request and get a simple routing decision.\n")

    request = input("User: ").strip().lower()
    if not request:
        print("Agent: No input received.")
        return

    if any(word in request for word in ["refund", "money back"]):
        route = "refund"
    elif any(word in request for word in ["delay", "late", "cancel", "canceled", "cancelled"]):
        route = "disruption"
    elif any(word in request for word in ["booking", "reservation"]):
        route = "booking"
    else:
        route = "general support"

    print(f"Agent: Routed to the {route} path.")


def run_constrained() -> None:
    from constrained_react.agent import run_agent

    run_agent()


def show_menu() -> None:
    print("\nTravel Support Agent Launcher")
    print("1) Reactive")
    print("2) Unconstrained ReAct")
    print("3) Routing")
    print("4) Constrained ReAct")
    print("5) Exit")


def main() -> None:
    actions: dict[str, Callable[[], None]] = {
        "1": run_reactive,
        "2": run_unconstrained,
        "3": run_routing,
        "4": run_constrained,
    }

    while True:
        show_menu()
        choice = input("Choose a model: ").strip()

        if choice == "5":
            print("Goodbye.")
            return

        action = actions.get(choice)
        if action is None:
            print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")
            continue

        try:
            action()
        except KeyboardInterrupt:
            print("\nCancelled. Returning to menu.")
        except Exception as exc:
            print(f"\nError: {exc}")


if __name__ == "__main__":
    main()