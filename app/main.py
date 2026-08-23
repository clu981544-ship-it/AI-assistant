from app.config import APP_NAME
from app.llm import chat


def main():
    print(f"应用：{APP_NAME}")
    print("输入 exit 退出")
    print("-" * 40)

    messages = []

    while True:
        user_input = input("你：")

        if user_input.lower() == "exit":
            print("程序结束")
            break

        messages.append({
            "role": "user",
            "content": user_input,
        })

        answer = chat(messages)

        messages.append({
            "role": "assistant",
            "content": answer,
        })

        print("AI：", answer)
        print()


if __name__ == "__main__":
    main()