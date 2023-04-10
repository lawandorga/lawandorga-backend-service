# from typing import Optional

# from pydantic import BaseModel


# class Car(BaseModel):
#     driver: Optional[str] = None
#     wheels: int


# car = Car(wheels=4)
# car.driver = "Max Maier"

# print(car)


class A:
    def __new__(cls, *args, **kwargs):
        print("A.__new__", cls, cls.mro())
        return super().__new__(cls)


class B(A):
    def __new__(cls, *args, **kwargs):
        print("B.__new__", cls, cls.mro())
        return super().__new__(cls)


class C(B):
    def __new__(cls, *args, **kwargs):
        print("C.__new__", cls, cls.mro())
        return super().__new__(cls)


c = C()
b = B()
