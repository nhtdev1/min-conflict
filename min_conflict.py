'''
Nguyễn Hoàng Thịnh - 17110372
Thuật toán Min-conflict algorithm sử dụng code mẫu của bài tập tuần 12
'''
# Solve N-queens problem using Min-conflicts algorithm
'''
YOUR TASKS:
1. Read to understand the following code 
2. Give comments on the min_conflicts() function to show your comprehensive understanding of the code
3. (Optional) Add GUI, animation...
'''

import random
import time

#%% Utilities:
def argmin_random_tie(seq, key=lambda x: x):
    """Return a minimum element of seq; break ties at random."""
    items = list(seq) # Là domain của biến var
    random.shuffle(items) # Ta xáo trộn các giá trị trong domain
    return min(items, key=key)# Chọn ra giá trị nhỏ nhaatst trong domain theo key. Trong đó
    # key là một hàm tính số lượng xung đột ứng với mỗi giá trị trong items ( mỗi giá trị trong items
    #là giá trị hàng )

class UniversalDict:
    """A universal dict maps any key to the same value. We use it here
    as the domains dict for CSPs in which all variables have the same domain.
    >>> d = UniversalDict(42)
    >>> d['life']
    42
    """      
    def __init__(self, value): self.value = value

    def __getitem__(self, key): return self.value

    def __repr__(self): return '{{Any: {0!r}}}'.format(self.value)


#%% CSP
class CSP():
    """This class describes finite-domain Constraint Satisfaction Problems.
    A CSP is specified by the following inputs:
        variables   A list of variables; each is atomic (e.g. int or string).
        domains     A dict of {var:[possible_value, ...]} entries.
        neighbors   A dict of {var:[var,...]} that for each variable lists
                    the other variables that participate in constraints.
        constraints A function f(A, a, B, b) that returns true if neighbors
                    A, B satisfy the constraint when they have values A=a, B=b
    """

    def __init__(self, variables, domains, neighbors, constraints):
        """Construct a CSP problem. If variables is empty, it becomes domains.keys()."""
        #super().__init__(())
        variables = variables or list(domains.keys())
        self.variables = variables
        self.domains = domains
        self.neighbors = neighbors
        self.constraints = constraints
        self.curr_domains = None
        self.nassigns = 0

    def assign(self, var, val, assignment):
        """Add {var: val} to assignment; Discard the old value if any."""
        assignment[var] = val
        self.nassigns += 1

    def unassign(self, var, assignment):
        """Remove {var: val} from assignment.
        DO NOT call this if you are changing a variable to a new value;
        just call assign for that."""
        if var in assignment:
            del assignment[var]

    def nconflicts(self, var, val, assignment):
        """Return the number of conflicts var=val has with other variables."""

        # Subclasses may implement this more efficiently
        def conflict(var2):
            return var2 in assignment and not self.constraints(var, val, var2, assignment[var2])

        return count(conflict(v) for v in self.neighbors[var])

    # This is for min_conflicts search  
    def conflicted_vars(self, current):
        """Hàm trả về danh sách các biến gây ra xung đột.
        Với mỗi biến ta sẽ xem biến đó cùng với giá trị hàng mà có, có tạo ra xung đột trên hàng, 
        chéo phụ, chéo chính hay không.
        Nếu kết quả trả về lớn hơn 0 thì biến đó và giá trị của nó gây ra xung đột, ta thêm nó
        vào danh sách. Ngược lại không """
        return [var for var in self.variables
                if self.nconflicts(var, current[var], current) > 0]


#%% N-queens problem
def queen_constraint(A, a, B, b):
    """Constraint is satisfied (true) if A, B are really the same variable,
    or if they are not in the same row, down diagonal, or up diagonal."""
    return A == B or (a != b and A + a != B + b and A - a != B - b)

class NQueensCSP(CSP):
    """
    Make a CSP for the nQueens problem for search with min_conflicts.
    Suitable for large n, it uses only data structures of size O(n).
    Think of placing queens one per column, from left to right.
    That means position (x, y) represents (var, val) in the CSP.
    The main structures are three arrays to count queens that could conflict:
        rows[i]      Number of queens in the ith row (i.e. val == i)
        downs[i]     Number of queens in the \ diagonal
                     such that their (x, y) coordinates sum to i
        ups[i]       Number of queens in the / diagonal
                     such that their (x, y) coordinates have x-y+n-1 = i
    """

    def __init__(self, n):
        """Initialize data structures for n Queens."""
        CSP.__init__(self, list(range(n)), UniversalDict(list(range(n))),
                     UniversalDict(list(range(n))), queen_constraint)
        '''
        Chúng ta có thể sử dụng vòng lặp lồng nhau để tính toán số lượng xung đột, do đó
        đối với mọi queens. Xung đột xảy ra khi:
        + Các queens nằm trong cùng một hàng
        + Các queens nằm trên cùng một đường chéo
        => Cách tiếp cận này mất O(n^2)

        Để đạt được độ phức tạp theo thời gian tuyến tính:
        Chúng ta sẽ sử dụng không gian O(n) để đặt được độ phức tạp thời gian tuyến tính trong
        kiểm tra xung đột. Ta sẽ biểu diễn bằng 3 mảng 1 chiều trông đó:
        rows: sẽ lưu trữ số lượng xung đột trong một hàng 
        VD: Ta có 4-queens như sau:
                        0   1   2   3
                    0       Q
                    1   Q       Q
                    2               Q
                    3
        rows: [1,2,1,0] - cho biết ở hàng 0 có 1 con hậu, hàng 1 có 2, 2 có 1, và 3 có 0

        Để kiểm tra xung đột chéo, chúng ta phải quan sát theo một cách khác.
        Trước tiên hay thử với đường chéo phụ. Xem hình ảnh sau trong đó mỗi ô của bảng
        chứa giá trị là tổng của cột và hàng:

        0   1   2   3   4   5   6   7
        1   2   3   4   5   6   7   8
        2   3   4   5   6   7   8   9
        3   4   5   6   7   8   9   10
        4   5   6   7   8   9  10   11
        5   6   7   8   9  10  11   12
        6   7   8   9  10  11  12   13
        7   8   9  10  11  12  13   14

        Nhìn vào hình ảnh trên ta sẽ thấy các đường chéo phụ sẽ có cùng giá trị tổng
        Đó là, nếu queen A đứng ở vị trí có giá trị là 10 và queen B đâu đó với giá trị 10, sẽ
        xảy ra xung đột!

        Cũng giống như rows, ta sẽ sử dụng mảng 1 chiều để biểu diễn số lượng xung đột. Nhưng 
        lần này kích thước sẽ gấp đôi. Vì giá trị tổng tối đa của chúng ta có thể là tổng của
        hàng cao nhất và cột cao nhất N+N.
        Ta biểu diển nó bằng mảng downs.

        Tương tự với đường chéo chính:
        7   8   9  10  11  12  13  14
        6   7   8   9  10  11  12  13
        5   6   7   8   9  10  11  12
        4   5   6   7   8   9  10  11
        3   4   5   6   7   8   9  10
        2   3   4   5   6   7   8   9
        1   2   3   4   5   6   7   8
        0   1   2   3   4   5   6   7

        Ta biểu diễn nó bằng mảng ups.             
        '''
        self.rows = [0] * n
        self.ups = [0] * (2 * n - 1)
        self.downs = [0] * (2 * n - 1)

    def nconflicts(self, var, val, assignment):
        """Hàm đếm số lượng các xung đột theo hàng, đường chéo dưới, đường chéo trên.
        Nếu trong assignment đã xuất hiện biến var cùng với giá trị hàng của nó, thì nó
        không thể xung đột với chính nó, ta trừ đi 3 (ứng với hàng, chéo phụ, chéo chính)"""
        n = len(self.variables)
        c = self.rows[val] + self.downs[var + val] + self.ups[var - val + n - 1]
        if assignment.get(var, None) == val:
            c -= 3
        return c

    def assign(self, var, val, assignment):
        """Assign var, and keep track of conflicts."""
        old_val = assignment.get(var, None) # Lấy ra giá trị hàng cũ của biến var
        if val != old_val: # Nếu giá trị hàng mới khác giá trị hàng cũ
            if old_val is not None:  # Ta kiểm tra nếu giá trị hàng cũ khác None thì 
            # ta sẽ hủy bỏ giá trị này đi, đồng thời xóa bỏ các xung đột gây ra bởi giá trị này
                self.record_conflict(assignment, var, old_val, -1)

            # Sau đó ta thêm giá trị hàng mới ứng với biến var vào trong assignment và
            # lưu lại xung đột của hàng này gây ra trên hàng, chéo phụ, chéo chính tương ứng
            self.record_conflict(assignment, var, val, +1)
            CSP.assign(self, var, val, assignment)

    def unassign(self, var, assignment):
        """Remove var from assignment (if it is there) and track conflicts."""
        if var in assignment:
            self.record_conflict(assignment, var, assignment[var], -1)
        CSP.unassign(self, var, assignment)

    def record_conflict(self, assignment, var, val, delta):
        """Ghi lại các xung đột gây ra bởi biến thêm hoặc xóa queen."""
        n = len(self.variables)
        self.rows[val] += delta
        self.downs[var + val] += delta
        self.ups[var - val + n - 1] += delta


#%% Min-conflicts for CSPs
''' READ AND COMMENT to show your comprehensive understanding of the following function '''
def min_conflicts(csp, max_steps=100000):
    """See Figure 6.8 for the algorithm"""
    # Đầu tiên là bước khởi tạo một complete assignment cho bài toán CSP
    csp.current = current = {}

    # Ta duyệt qua tất cả các biến (var: cột)
    for var in csp.variables:
        # Lấy ra giá trị hàng làm cho var (cột) tạo ra ít xung đột nhất trong current
        val = min_conflicts_value(csp, var, current)
        # Gán giá trị hàng ứng với biến var vào trong current
        csp.assign(var, val, current)
    
    for i in range(max_steps):
        # Lấy ra danh sách các cột gây ra xung đột
        conflicted = csp.conflicted_vars(current)
        # Nếu danh sách không tồn tại có nghĩa là không có cột nào gây ra xung đột
        # ta sẽ trả về complete assigment
        if not conflicted:
            return current
        # Ta chọn ngẫu nhiên một cột trong danh sách các cột gây ra xung đột
        var = random.choice(conflicted)

        # Chọn ra giá trị val(hàng) trên cột(var) trong trạng thái hiện tại (current) sao 
        # cho giá trị val(hàng) sẽ tạo ra ít xung đột giữa các queens nhất.
        val = min_conflicts_value(csp, var, current)
        # Gán giá trị này cho biến var
        csp.assign(var, val, current)
    return None

def min_conflicts_value(csp, var, current):
    """Hàm này sẽ trả về giá trị hàng sẽ cung cấp cho var(cột) tạo ra số lượng xung đột ít nhất
    . Nếu trên cột đó có nhiều giá trị hàng tạo ra ít xung đột như nhau, ta chọn ngẫu nhiện một"""
    return argmin_random_tie(csp.domains[var], key=lambda val: csp.nconflicts(var, val, current))


#%% main
if __name__ == '__main__':      
    problem = NQueensCSP(n=8)
    min_conflicts(problem, max_steps=100000); 
    print(problem.current);
    
    '''
    Hàm trả về kết quả vị trí đặt các quân hậu và tổng thời gian mà nó tìm kiếm ra solution
    '''
def getResults(numberOfQueens):
    startTime = time.time()
    problem = NQueensCSP(n=numberOfQueens)
    results = min_conflicts(problem, max_steps=100000); 
    return results, time.time() - startTime