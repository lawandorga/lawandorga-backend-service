from core.timeline.utils import camel_to_snake_case


def test_camel_to_snake_case():
    assert camel_to_snake_case("CamelCase") == "camel_case"
    assert camel_to_snake_case("Camel") == "camel"
    assert camel_to_snake_case("camel_correct") == "camel_correct"
    assert camel_to_snake_case("This_is-ReallyWerid") == "this_is-really_werid"
