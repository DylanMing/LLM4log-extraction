import importlib

def import_prompt_components(prompt_file):
    module_name = prompt_file
    module = importlib.import_module(module_name)

    return (
        module.system_instruction,
        module.parameters,
        module.response_schema,
        module.context,
        module.safety_config,
    )

# 用法示例
if __name__ == "__main__":
    prompt_file = "prompt.prompt"  # 根据需要设置为True或False

    # 导入相应的内容
    system_instruction, parameters, response_schema, context, safety_config = import_prompt_components(prompt_file)

    # 测试输出
    print("System Instruction:", system_instruction)
    print("Parameters:", parameters)
    print("Response Schema:", response_schema)
    print("Context:", context)
    print("Safety Config:", safety_config)
