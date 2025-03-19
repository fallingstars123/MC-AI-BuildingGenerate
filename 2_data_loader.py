import torch
import torch.nn as nn
import torch.nn.functional as F

class ConvBlock3D(nn.Module):
    """3D 卷积 + BN + ReLU"""
    def __init__(self, in_channels, out_channels):
        super(ConvBlock3D, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv3d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm3d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.conv(x)


class UNet3D(nn.Module):
    """简化版 3D U-Net"""
    def __init__(self, in_channels=1, out_channels=1, features=[32, 64, 128]):
        super(UNet3D, self).__init__()

        # 编码器部分（下采样）
        self.encoders = nn.ModuleList([
            ConvBlock3D(in_channels, features[0]),
            ConvBlock3D(features[0], features[1]),
            ConvBlock3D(features[1], features[2])
        ])
        self.pool = nn.MaxPool3d(2)

        # Bottleneck 层
        self.bottleneck = ConvBlock3D(features[2], features[2] * 2)

        # 解码器部分（上采样）
        self.upconvs = nn.ModuleList([
            nn.ConvTranspose3d(features[2] * 2, features[2], kernel_size=2, stride=2),
            nn.ConvTranspose3d(features[2], features[1], kernel_size=2, stride=2),
            nn.ConvTranspose3d(features[1], features[0], kernel_size=2, stride=2)
        ])
        self.decoders = nn.ModuleList([
            ConvBlock3D(features[2] * 2, features[2]),
            ConvBlock3D(features[1] * 2, features[1]),
            ConvBlock3D(features[0] * 2, features[0])
        ])

        # 最终输出层
        self.final_conv = nn.Conv3d(features[0], out_channels, kernel_size=1)

    def forward(self, x):
        # 编码器（下采样）
        enc_outputs = []
        for encoder in self.encoders:
            x = encoder(x)
            enc_outputs.append(x)
            x = self.pool(x)

        # Bottleneck
        x = self.bottleneck(x)

        # 解码器（上采样）
        for i in range(len(self.decoders)):
            x = self.upconvs[i](x)
            x = torch.cat([x, enc_outputs[-(i+1)]], dim=1)  # 跳跃连接
            x = self.decoders[i](x)

        return self.final_conv(x)

# 测试模型
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = UNet3D(in_channels=1, out_channels=1).to(device)

dummy_input = torch.randn(1, 1, 10, 10, 10).to(device)  # batch_size=1，单通道，10x10x10
output = model(dummy_input)

print("输入形状:", dummy_input.shape)
print("输出形状:", output.shape)
