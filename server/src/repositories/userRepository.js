// Mock Data and Repository Layer
const users = [
    { id: 1, name: 'Alice', role: 'commuter' },
    { id: 2, name: 'Bob', role: 'driver' },
    { id: 3, name: 'Charlie', role: 'admin' }
];

class UserRepository {
    findAll() {
        return Promise.resolve(users);
    }

    findById(id) {
        const user = users.find(u => u.id === parseInt(id));
        return Promise.resolve(user);
    }
}

module.exports = new UserRepository();
