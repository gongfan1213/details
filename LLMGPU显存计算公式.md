Memory(GB) = P * (Q/8)  * (1 + Overhead)

P是参数数量（十亿)

Q是位精度的（如FP16是16位）

Q/8 将位转换成为字节的

Overhead是额外的开销的，通常是20%，包括KV缓存，激活缓冲区等

70B的模型使用FP16的精度

70* （16/8） * 1.2 = 168GB

<img width="881" height="743" alt="image" src="https://github.com/user-attachments/assets/524c173f-aa56-467d-96fb-fa41978831c1" />


<img width="675" height="743" alt="image" src="https://github.com/user-attachments/assets/d02e727b-8f03-4397-9c8d-dafefc32154d" />
