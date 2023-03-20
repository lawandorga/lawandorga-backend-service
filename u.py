# import os
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
# try:
#     from django.core.management import execute_from_command_line
# except ImportError as exc:
#     raise ImportError(
#         "Couldn't import Django. Are you sure it's installed and "
#         "available on your PYTHONPATH environment variable? Did you "
#         "forget to activate a virtual environment?"
#     ) from exc
# execute_from_command_line()
#
# from inspect import signature
# from typing import List, Optional
#
# from opyoid import ClassBinding, Injector, InstanceBinding, SelfBinding
#
#
# class UserMessageSource:
#     def get_user_message(self) -> str:
#         raise NotImplementedError
#
#
# class OutputWriter:
#     def write_bot_messages(self, bot_messages: List[str]) -> None:
#         raise NotImplementedError
#
#

# class AnswerGenerator:
#     def __init__(self):
#         self.end_conversation = False
#
#     def get_answers(self, user_message: str) -> List[str]:
#         bot_messages = []
#         if user_message in ["hello", "hi"]:
#             bot_messages.append("Hello there!")
#         elif user_message in ["bye", "good bye"]:
#             bot_messages.append("See you!")
#             self.end_conversation = True
#         else:
#             bot_messages.append("I'm sorry, I didn't understand that :(")
#         return bot_messages
#
#
# class ConversationLogger:
#     def __init__(self, file_path: str):
#         self.file_path = file_path
#
#     def append_to_conversation(
#         self, user_message: str, bot_messages: List[str]
#     ) -> None:
#         with open(self.file_path, "a") as conversation_file:
#             conversation_file.write(f"Human: {user_message}\n")
#             for message in bot_messages:
#                 conversation_file.write(f"Bot: {message}\n")
#
#
# class Chat:
#     def __init__(
#         self,
#         user_message_source: UserMessageSource,
#         output_writer: OutputWriter,
#         answer_generator: AnswerGenerator,
#         conversation_logger: Optional[ConversationLogger] = None,
#     ):
#         self.user_message_source = user_message_source
#         self.output_writer = output_writer
#         self.answer_generator = answer_generator
#         self.conversation_logger = conversation_logger
#
#     def run(self):
#         while not self.answer_generator.end_conversation:
#             user_message = self.user_message_source.get_user_message()
#             bot_messages = self.answer_generator.get_answers(user_message)
#             self.output_writer.write_bot_messages(bot_messages)
#             if self.conversation_logger:
#                 self.conversation_logger.append_to_conversation(
#                     user_message, bot_messages
#                 )
#
#
# ###
# # IMPL
# ###
# class CliUserMessageSource(UserMessageSource):
#     def get_user_message(self) -> str:
#         return input("Human: ").strip().lower()
#
#
# class CliOutputWriter(OutputWriter):
#     def write_bot_messages(self, bot_messages: List[str]) -> None:
#         for message in bot_messages:
#             print(f"Bot: {message}")
#
#
# ###
# # RUN
# ###
# # if __name__ == "__main__":
# #     injector = Injector(bindings=[
# #         SelfBinding(Chat),
# #         SelfBinding(AnswerGenerator),
# #         InstanceBinding(ConversationLogger, ConversationLogger("file.txt")),
# #         ClassBinding(UserMessageSource, bound_class=CliUserMessageSource),
# #         # ClassBinding(OutputWriter, bound_class=CliOutputWriter),
# #     ])
# #     chat = injector.inject(Chat)
# #     chat.run()
#
#
# class Depends:
#     def __init__(self, f):
#         self.f = f
#
#
# def get_c():
#     return "c"
#
#
# def my_func(a: int, b: str, c=Depends(get_c)):
#     pass
#
#
# def run():
#     from config.api import get_org_user
#
#     s = signature(get_org_user)
#     parameters = s.parameters.values()
#     for parameter in parameters:
#         print(parameter.kind)
#         print(parameter)
#
#
# run()
