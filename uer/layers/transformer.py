import torch.nn as nn
from uer.layers.layer_norm import LayerNorm
from uer.layers.position_ffn import PositionwiseFeedForward
from uer.layers.multi_headed_attn import MultiHeadedAttention


class TransformerLayer(nn.Module):
    """
    Transformer layer mainly consists of two parts:
    multi-headed self-attention and feed forward layer.
    """
    def __init__(self, args):
        super(TransformerLayer, self).__init__()

        # Multi-headed self-attention.
        self.self_attn = MultiHeadedAttention(
            args.hidden_size, args.heads_num, args.dropout
        )
        self.dropout_1 = nn.Dropout(args.dropout)
        self.layer_norm_1 = LayerNorm(args.hidden_size)
        # Feed forward layer.
        self.feed_forward = PositionwiseFeedForward(
            args.hidden_size, args.feedforward_size, args.hidden_act
        )
        self.dropout_2 = nn.Dropout(args.dropout)
        self.layer_norm_2 = LayerNorm(args.hidden_size)

    def forward(self, hidden, mask):
        """
        Args:
            hidden: [batch_size x seq_length x emb_size]
            mask: [batch_size x 1 x seq_length x seq_length]
        Returns:
            output: [batch_size x seq_length x hidden_size]
        """
        inter = self.dropout_1(self.self_attn(hidden, hidden, hidden, mask))
        inter = self.layer_norm_1(inter + hidden)
        output = self.dropout_2(self.feed_forward(inter))
        output = self.layer_norm_2(output + inter)  
        return output

class GptBlock(nn.Module):
    def __init__(self, args):
        super(GptBlock, self).__init__()

        # Multi-headed self-attention.
        self.self_attn = MultiHeadedAttention(
            args.hidden_size, args.heads_num, args.dropout
        )
        self.layer_norm_1 = LayerNorm(args.hidden_size)
        # Feed forward layer.
        self.feed_forward = PositionwiseFeedForward(
            args.hidden_size, args.feedforward_size, args.hidden_act
        )
        self.layer_norm_2 = LayerNorm(args.hidden_size)

    def forward(self, hidden, mask):
        """
        Args:
            hidden: [batch_size x seq_length x emb_size]
            mask: [batch_size x 1 x seq_length x seq_length]
        Returns:
            output: [batch_size x seq_length x hidden_size]
        """
        inter = self.layer_norm_1(hidden)
        inter = self.self_attn(inter, inter, inter, mask)
        hidden = hidden + inter
        output = self.layer_norm_2(hidden) 
        output = self.feed_forward(output)
        
        return output + hidden

class T5Decoder(nn.Module):
    def __init__(self, args):
        super(T5Decoder, self).__init__()

        self.self_attn1 = MultiHeadedAttention(
            args.hidden_size, args.heads_num, args.dropout
        )
        self.self_attn2 = MultiHeadedAttention(
            args.hidden_size, args.heads_num, args.dropout
        )
        self.layer_norm_1 = LayerNorm(args.hidden_size)
        self.layer_norm_2 = LayerNorm(args.hidden_size)
        self.layer_norm_3 = LayerNorm(args.hidden_size)
        self.feed_forward = PositionwiseFeedForward(
            args.hidden_size, args.feedforward_size, args.hidden_act
        )

    def forward(self, hidden, encoder_hidden, mask):
        """
        Args:
            emb: [batch_size x seq_length x emb_size]
            hidden: [batch_size x seq_length x emb_size]
            mask: [batch_size x 1 x seq_length x seq_length]
        Returns:
            output: [batch_size x seq_length x hidden_size]
        """
        x = hidden
        inter = self.layer_norm_1(hidden)
        inter = self.self_attn1(inter, inter, inter, mask)
        inter = x + inter
        x = inter
        inter = self.layer_norm_2(inter)
        inter = self.self_attn2(encoder_hidden, encoder_hidden, inter, mask)
        inter = x + inter
        x = inter
        inter = self.layer_norm_3(inter)
        inter = self.feed_forward(inter)

        return x + inter
