class Solution
{
public:
    int maxSubArray(vector<int>& nums)
    {
        if (nums.empty()) return 0; // Edge case: empty array

        int maxEndingHere = nums[0]; // Maximum sum of subarray ending at current position
        int maxSoFar = nums[0];     // Global maximum sum found so far

        for (size_t i = 1; i < nums.size(); ++i)
        {
            // Decide whether to continue the current subarray or start a new one
            maxEndingHere = max(nums[i], maxEndingHere + nums[i]);
            // Update the global maximum sum
            maxSoFar = max(maxSoFar, maxEndingHere);
        }

        return maxSoFar;
    }
};