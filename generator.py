import torch
import torch.nn as nn

class block(nn.Module):
    def __init__(self,input_channels,output_channels, down = True, act = "relu", use_dropout = False):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(input_channels, output_channels,4,2,1, bias = False, padding_mode = "reflect")
            if down else
            nn.ConvTranspose2d(input_channels, output_channels,4,2,1, bias = False),
            nn.InstanceNorm2d(output_channels, affine = True ),
            nn.ReLU() if act == "relu" else nn.LeakyReLU(0.2)
        )
        
        self.use_dropout = use_dropout
        self.Dropout = nn.Dropout(0.5)
    
    def forward(self,x):
        x = self.conv(x)
        return self.Dropout(x) if self.use_dropout else x
    
class Generator(nn.Module):
    def __init__(self,input_channels,features = 64):
        super().__init__()
        
        self.initial_down = nn.Sequential(
            nn.Conv2d(input_channels, features ,4,2,1, padding_mode = "reflect"),
            nn.LeakyReLU(0.2)
            )
        
        self.down1 = block(features, features*2, down = True, act = "leaky", use_dropout = False)
        self.down2 = block(features*2, features*4, down = True, act = "leaky", use_dropout = False)
        self.down3 = block(features*4, features*8, down = True, act = "leaky", use_dropout = False)
        self.down4 = block(features*8, features*8, down = True, act = "leaky", use_dropout = False)
        self.down5 = block(features*8, features*8, down = True, act = "leaky", use_dropout = False)
        self.down6 = block(features*8, features*8, down = True, act = "leaky", use_dropout = False)
        
        self.bottleneck = nn.Sequential(
            nn.Conv2d(features*8,features*8,4,2,1, padding_mode = "reflect"),
            nn.LeakyReLU(0.2)
        )
        
        self.up1 = block(features*8, features*8, down = False, act = "relu", use_dropout = True)
        self.up2 = block(features*8*2, features*8, down = False, act = "relu", use_dropout = True)
        self.up3 = block(features*8*2, features*8, down = False, act = "relu", use_dropout = True)
        self.up4 = block(features*8*2, features*8, down = False, act = "relu", use_dropout = True)
        self.up5 = block(features*8*2, features*4, down = False, act = "relu", use_dropout = False)
        self.up6 = block(features*4*2, features*2, down = False, act = "relu", use_dropout = False)
        self.up7 = block(features*2*2, features, down = False, act = "relu", use_dropout = False)
        
        self.final_up = nn.Sequential(
            nn.ConvTranspose2d(features*2,input_channels,4,2,1),
            nn.Tanh()
        )
        
    def forward(self,x):
        d1 = self.initial_down(x)
        d2 = self.down1(d1)
        d3 = self.down2(d2)
        d4 = self.down3(d3)
        d5 = self.down4(d4)
        d6 = self.down5(d5)
        d7 = self.down6(d6)
        
        bottleneck = self.bottleneck(d7)
                
        up1 = self.up1(bottleneck)
        up2 = self.up2(torch.cat([up1,d7],dim = 1))
        up3 = self.up3(torch.cat([up2,d6],dim = 1))
        up4 = self.up4(torch.cat([up3,d5],dim = 1))
        up5 = self.up5(torch.cat([up4,d4],dim = 1))
        up6 = self.up6(torch.cat([up5,d3],dim = 1))
        up7 = self.up7(torch.cat([up6,d2],dim = 1))
        final_up = self.final_up(torch.cat([up7,d1],dim = 1))
        
        return final_up
    
def test():
    x = torch.randn(1,1,256,256)
    model = Generator(input_channels = 1, features = 64)
    x = model(x)
    print(x.shape)

if __name__ == "__main__":
    test()