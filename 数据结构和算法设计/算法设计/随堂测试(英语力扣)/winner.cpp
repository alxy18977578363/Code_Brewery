class Solution
{
public:
    int findTheWinner(int n, int k)
    {
        vector<int> friends(n);
        for (int i = 0; i < n; ++i)
        {
            friends[i] = i + 1;  // Initialize friends from 1 to n
        }

        int index = 0;  // Start at the first friend

        while (friends.size() > 1)
        {
            // Calculate the index of the friend to be removed
            index = (index + k - 1) % friends.size();

            // Remove the friend from the circle
            friends.erase(friends.begin() + index);
        }

        return friends[0];  // The last remaining friend is the winner
    }
};