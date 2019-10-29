from typing import List, Dict
from pydantic import BaseModel

class Parent(BaseModel):
	p_attr : List = []

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		print("I AM DOING PARENT STUFF")

class Child(Parent):

	c_attr1 : str
	c_attr2 : str = "hi"
	c_attr3 : int = 0

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.p_attr.append(1)

	def child_method(self):
		print(dict(self))


def test_classes():
	test_child = Child(c_attr1 = "hello")

	test_child.child_method()