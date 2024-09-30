#include <functional>
#include <iostream>
#include <iomanip>
#include <vector>
using namespace std;

struct MYArray {
  int rows, cols;
  vector<vector<double>> data;
};

void reshape(int rows, int cols, MYArray &arr) {
  arr.rows = rows;
  arr.cols = cols;
  arr.data.resize(rows);
  for (int i = 0; i < rows; ++i) {
    arr.data[i].resize(cols);
  }
}
void read(MYArray &arr) {
  // TODO
  int rows, cols = 0;
  cin >> rows >> cols;
  reshape(rows, cols, arr);
  for (int i = 0; i < rows; i++) {
    for (int j = 0; j < cols; j++) {
      int data;
      cin >> data;
      arr.data[i][j] = data;
    }
  }
  return;
  // END TODO
}
MYArray divide(double x, MYArray &arr) {
  // TODO
  MYArray result = arr;
  for (int i = 0; i < arr.rows; i++) {
    for (int j = 0; j < arr.cols; j++) {
      result.data[i][j] /= x;
    }
  }
  return result;
  // END TODO
}
MYArray T(MYArray &arr) {
  MYArray result;
  reshape(arr.cols, arr.rows, result);
  for (int i = 0; i < arr.rows; ++i) {
    for (int j = 0; j < arr.cols; ++j) {
      result.data[j][i] = arr.data[i][j];
    }
  }
  return result;
}
void print(MYArray &arr) {
  for (int i = 0; i < arr.rows; ++i) {
    for (int j = 0; j < arr.cols; ++j) {
      cout << fixed << setprecision(3) << arr.data[i][j] << " ";
    }
  }
}

MYArray apply(function<double(double, double)> f, int axis, MYArray &arr) {
  // TODO
  int rows = arr.rows;
  int cols = arr.cols;
  MYArray result;
  reshape(rows, cols, result);
  if (axis == -1) {
    double a = arr.data[0][0];
    for (int i = 0; i < arr.rows; i++) {
      for (int j = 0; j < arr.cols; j++) {
        a = f(arr.data[i][j], a);
      }
    }
    result.data[0][0] = a;

  } else if (axis == 0) {
    for (int i = 0; i < arr.cols; i++) {
      double a = arr.data[0][0];
      for (int j = 0; j < arr.rows; j++) {
        a = f(arr.data[j][i], a);
      }
      result.data[0][i] = a;
    }
    reshape(1, cols, result);
  } else if (axis == 1) {
    for (int i = 0; i < arr.rows; i++) {
      double a = arr.data[0][0];
      for (int j = 0; j < arr.cols; j++) {
        a = f(arr.data[i][j], a);
      }
      result.data[i][0] = a;
    }
    reshape(rows, 1, result);
  }
  return result;
  // END TODO
}

double MAX(double a, double b) {
  return max(a, b);
}
double MIN(double a, double b) {
  return min(a, b);
}
double SUM(double a, double b) {
  return a + b;
}

void Solve() {
  // TODO
  MYArray arr;
  int q;
  read(arr);
  cin >> q;

  if (q == 1) {
    auto result = apply(MAX, -1, arr);
    cout << fixed << setprecision(3) << result.data[0][0];
  } else if (q == 2) {
    auto result = apply(MIN, -1, arr);
    cout << fixed << setprecision(3) << result.data[0][0];
  } else if (q == 3) {
    int total = arr.cols * arr.rows;
    auto result = apply(SUM, -1, arr);
    cout << fixed << setprecision(3) << result.data[0][0] / total;
  } else if (q == 4) {
    auto a = apply(SUM, 1, arr);
    auto result = divide(arr.cols, a);
    print(result);
  } else if (q == 5) {
    auto T_arr = T(arr);
    auto a = apply(SUM, 1, T_arr);
    auto result = divide(arr.rows, a);
    print(result);
  }
  // END TODO
}
int main() {
  Solve();
  return 0;
}
