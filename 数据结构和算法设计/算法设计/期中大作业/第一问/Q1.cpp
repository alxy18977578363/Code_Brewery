#include <iostream>
#include <fstream>
#include <vector>
#include <algorithm>
#include <random>
#include <string>

using namespace std;

// Student data structure
struct Student
{
    string id;
    string name;
    int chinese;
    int math;
    int english;
    int total;

    Student(string id, string name, int c, int m, int e)
        : id(id), name(name), chinese(c), math(m), english(e), total(c + m + e)
    {
    }
};

// Custom comparator for sorting
bool compareStudents(const Student& a, const Student& b)
{
    if (a.total != b.total) return a.total > b.total;
    if (a.chinese != b.chinese) return a.chinese > b.chinese;
    if (a.math != b.math) return a.math > b.math;
    return a.english > b.english;
}

// Generate random scores between 0 and 150
int generateRandomScore(mt19937& gen)
{
    uniform_int_distribution<> dist(0, 150);
    return dist(gen);
}

// Generate random student data
vector<Student> generateStudentData(int n)
{
    vector<Student> students;
    random_device rd;
    mt19937 gen(rd());

    for (int i = 0; i < n; ++i)
    {
        string id = "S" + to_string(1000000 + i).substr(1);
        string name = "Student_" + to_string(i + 1);

        int chinese = generateRandomScore(gen);
        int math = generateRandomScore(gen);
        int english = generateRandomScore(gen);

        students.emplace_back(id, name, chinese, math, english);
    }

    return students;
}

// Write student data to file
void writeToFile(const vector<Student>& students, const string& filename)
{
    ofstream outFile(filename);
    if (!outFile)
    {
        cerr << "Error opening output file!" << endl;
        return;
    }

    outFile << "排名,考号,姓名,总分,语文,数学,英语\n";
    for (size_t i = 0; i < students.size(); ++i)
    {
        const auto& s = students[i];
        outFile << i + 1 << "," << s.id << "," << s.name << ","
            << s.total << "," << s.chinese << "," << s.math << "," << s.english << "\n";
    }

    outFile.close();
    cout << "Results written to " << filename << endl;
}

int main()
{
    int n;
    cout << "Enter number of students: ";
    cin >> n;

    // Generate student data
    vector<Student> students = generateStudentData(n);

    // Sort students
    sort(students.begin(), students.end(), compareStudents);

    // Write to file
    writeToFile(students, "student_rankings.csv");

    return 0;
}