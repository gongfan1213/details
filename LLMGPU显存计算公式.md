<img width="710" height="383" alt="image" src="https://github.com/user-attachments/assets/392d8a6e-87c6-49b7-af50-4f495154ff16" />

<img width="658" height="407" alt="image" src="https://github.com/user-attachments/assets/06326eac-58fa-4b29-85e4-93a89b584b49" />

<img width="680" height="401" alt="image" src="https://github.com/user-attachments/assets/23b203a5-2097-4f3c-bfe8-c6d498695545" />


Memory(GB) = P * (Q/8)  * (1 + Overhead)

P是参数数量（十亿)

Q是位精度的（如FP16是16位）

Q/8 将位转换成为字节的

Overhead是额外的开销的，通常是20%，包括KV缓存，激活缓冲区等

70B的模型使用FP16的精度

70* （16/8） * 1.2 = 168GB

<img width="881" height="743" alt="image" src="https://github.com/user-attachments/assets/524c173f-aa56-467d-96fb-fa41978831c1" />


<img width="675" height="743" alt="image" src="https://github.com/user-attachments/assets/d02e727b-8f03-4397-9c8d-dafefc32154d" />
