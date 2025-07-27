#include "HuffmanTree.h"

HuffmanTree::HuffmanTree(bool isLeaf,bool isSelected,int weight,QString keyWord,int parent,int leftChild,int rightChild,int pos){
    //设置对应的值
    this->isLeaf=isLeaf;
    this->isSelected=isSelected;
    this->weight=weight;
    this->keyWord=keyWord;
    this->parent=parent;
    this->leftChild=leftChild;
    this->rightChild=rightChild;
    this->pos=pos;
}
HuffmanTree::~HuffmanTree(){
}
