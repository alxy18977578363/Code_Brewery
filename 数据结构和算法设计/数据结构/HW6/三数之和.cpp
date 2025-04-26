#include<vector>
#include<iostream>
#include<algorithm>
using namespace std;

/* 个人的思考：为什么双指针法一定可以呢？我认为，应该结合数列本身的性质和操作的性质。sort之后数列从小到大，一开始left和right在极限两侧。此时进行的操作是小了就右移左指针，大了就左移右指针。因此一路走来，右移右指针和左移左指针就“不靠谱”，因为那是朝着不平的方向去的 */

class Solution {
public:
    vector<vector<int>> threeSum(vector<int>& nums) {
        int n = nums.size();
        if (n <= 2) return {}; // 返回空二维向量

        sort(nums.begin(), nums.end()); // 排序
        vector<vector<int>> result;

        for (int i = 0; i < n - 2; i++) {
            // 跳过重复的 nums[i]
            if (i > 0 && nums[i] == nums[i - 1]) continue;

            int left = i + 1;
            int right = n - 1;

            while (left < right) {
                int sum = nums[i] + nums[left] + nums[right];
                if (sum < 0) {
                    left++;
                } else if (sum > 0) {
                    right--;
                } else {
                    result.push_back({nums[i], nums[left], nums[right]});

                    // 跳过重复的 nums[left] 和 nums[right]
                    while (left < right && nums[left] == nums[left + 1]) left++;
                    while (left < right && nums[right] == nums[right - 1]) right--;

                    // 移动指针
                    left++;
                    right--;
                }
            }
        }

        return result;
    }
};


int main()
{
    int n;
    cin >> n;
    
    if (n <= 2)    return 0;        // 错误处理

    /* 数组 */
    vector<int>arr(n,-1);
    for (int i = 0; i < n; i++)
    {
        cin >> arr[i];
    }
    Solution solution;
    vector<vector<int>> result = solution.threeSum(arr);

    /* 输出结果 */
    for (const auto& nums : result)
    {
        for (const auto& num : nums)
        {
            cout << num << " ";
        }
        cout << endl;
    }
}
