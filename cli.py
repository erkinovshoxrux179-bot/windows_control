"""
CLI sinov rejimi — UI va mikrofonsiz, faqat matn orqali tekshirish.

API kalitingiz va NLU to'g'ri ishlayotganini tez tekshirish uchun:
    python cli.py

So'ng buyruqlarni o'zbekcha yozing. Chiqish: "chiqish" yoki Ctrl+C.
Eslatma: amallar (open_app va h.k.) faqat Windows'da to'liq ishlaydi.
"""

from brain import nlu
from actions import executor


def main():
    print("Windows Controller — CLI sinov rejimi")
    print("Buyruqni o'zbekcha yozing (chiqish uchun: 'chiqish')\n")
    while True:
        try:
            text = input("siz> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nXayr!")
            break
        if text.lower() in ("chiqish", "exit", "quit"):
            print("Xayr!")
            break
        if not text:
            continue

        command = nlu.parse(text)
        print(f"  [NLU]  action={command['action']}  params={command['params']}")
        result = executor.execute(command)
        print(f"  bot> {result}\n")


if __name__ == "__main__":
    main()
