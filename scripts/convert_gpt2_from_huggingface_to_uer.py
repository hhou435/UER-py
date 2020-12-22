import torch
import argparse
import collections
import re

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--input_model_path", type=str, default="pytorch_model.bin",
                        help=".")
parser.add_argument("--input_vocab_path", type=str, default="vocab.txt",
                        help=".")
parser.add_argument("--output_model_path", type=str, default="gpt_model.bin",
                        help=".")

parser.add_argument("--layers", type=int, default=12)

args = parser.parse_args()
path = args.input_model_path

input_model = torch.load(args.input_model_path)

output_model = collections.OrderedDict()


output_model["embedding.word_embedding.weight"] = input_model["transformer.wte.weight"]
output_model["embedding.position_embedding.weight"] = input_model["transformer.wpe.weight"]

for i in range(args.layers):
    if i == 0:
        print(input_model["transformer.h." + str(i) + ".attn.c_attn.weight"].t()[0:768,:].sum().mean())
        
    for j in range(3):
        output_model["encoder.transformer." + str(i) + ".self_attn.linear_layers." + str(j) + ".weight"] = input_model["transformer.h." + str(i) + ".attn.c_attn.weight"].t()[j*768:(j+1)*768,:]
        output_model["encoder.transformer." + str(i) + ".self_attn.linear_layers." + str(j) + ".bias"] = input_model["transformer.h." + str(i) + ".attn.c_attn.bias"][j*768:(j+1)*768]
    if i == 0:
        print(output_model["encoder.transformer." + str(i) + ".self_attn.linear_layers.0.weight"].sum().mean())

    output_model["encoder.transformer." + str(i) + ".self_attn.final_linear.weight"] = input_model["transformer.h." + str(i) + ".attn.c_proj.weight"].t()
    output_model["encoder.transformer." + str(i) + ".self_attn.final_linear.bias"] = input_model["transformer.h." + str(i) + ".attn.c_proj.bias"]

    output_model["encoder.transformer." + str(i) + ".layer_norm_1.gamma"] = input_model["transformer.h." + str(i) + ".ln_1.weight"]
    output_model["encoder.transformer." + str(i) + ".layer_norm_1.beta"] = input_model["transformer.h." + str(i) + ".ln_1.bias"]

    output_model["encoder.transformer." + str(i) + ".feed_forward.linear_1.weight"] = input_model["transformer.h." + str(i) + ".mlp.c_fc.weight"].t()
    output_model["encoder.transformer." + str(i) + ".feed_forward.linear_1.bias"] = input_model["transformer.h." + str(i) + ".mlp.c_fc.bias"]
    output_model["encoder.transformer." + str(i) + ".feed_forward.linear_2.weight"] = input_model["transformer.h." + str(i) + ".mlp.c_proj.weight"].t()
    output_model["encoder.transformer." + str(i) + ".feed_forward.linear_2.bias"] = input_model["transformer.h." + str(i) + ".mlp.c_proj.bias"]

    output_model["encoder.transformer." + str(i) + ".layer_norm_2.gamma"] = input_model["transformer.h." + str(i) + ".ln_2.weight"]
    output_model["encoder.transformer." + str(i) + ".layer_norm_2.beta"] = input_model["transformer.h." + str(i) + ".ln_2.bias"]


output_model["encoder.layer_norm.gamma"] = input_model["transformer.ln_f.weight"]
output_model["encoder.layer_norm.beta"] = input_model["transformer.ln_f.bias"]
output_model["target.output_layer.weight"] = input_model["lm_head.weight"]
output_model["target.output_layer.bias"] = torch.zeros([21128])

torch.save(output_model, 'pytorch_model.bin')
