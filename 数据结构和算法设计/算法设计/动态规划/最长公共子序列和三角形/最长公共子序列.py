import os
import sys

class Solution:
    def longestCommonSubsequence(self, text1: str, text2: str) -> int:
        m = len(text1)          # 表长1
        n = len(text2)          # 表长2
        dp = [[0 for j in range(n + 1)] for i in range(m + 1)]

        for i in range(m):
            for j in range(n):
                if text1[i] == text2[j]:
                    dp[i + 1][j + 1] = dp[i][j] + 1
                else:
                    dp[i + 1][j + 1] = max(dp[i][j + 1],dp[i + 1][j])

        return dp[m][n]