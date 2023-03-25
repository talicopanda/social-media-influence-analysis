def calcualate_embedding_bin(self, vector):
    return (((dimension // self.bin_size ) * self.bin_size) for dimension in vector)
