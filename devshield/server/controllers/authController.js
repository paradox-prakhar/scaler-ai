import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import User from '../models/User.js';
import mongoose from 'mongoose';

const generateToken = (id) => {
  return jwt.sign({ id }, process.env.JWT_SECRET || 'devshield-secret-1234', {
    expiresIn: '30d',
  });
};

// In-memory array fallback if MongoDB is not running locally for the hackathon
const memoryUsers = [];

export const registerUser = async (req, res) => {
  const { username, email, password } = req.body;

  if (mongoose.connection.readyState !== 1) {
     const exists = memoryUsers.find(u => u.email === email);
     if (exists) return res.status(400).json({ message: 'User already exists' });
     const newUser = { _id: Date.now().toString(), username, email, password };
     memoryUsers.push(newUser);
     return res.status(201).json({
        _id: newUser._id,
        username: newUser.username,
        email: newUser.email,
        token: generateToken(newUser._id)
     });
  }

  const userExists = await User.findOne({ email });
  if (userExists) {
    return res.status(400).json({ message: 'User already exists' });
  }

  const salt = await bcrypt.genSalt(10);
  const hashedPassword = await bcrypt.hash(password, salt);

  const user = await User.create({
    username,
    email,
    password: hashedPassword,
  });

  if (user) {
    res.status(201).json({
      _id: user._id,
      username: user.username,
      email: user.email,
      token: generateToken(user._id),
    });
  } else {
    res.status(400).json({ message: 'Invalid user data' });
  }
};

export const loginUser = async (req, res) => {
  const { email, password } = req.body;

  if (mongoose.connection.readyState !== 1) {
    const user = memoryUsers.find(u => u.email === email && u.password === password);
    if (user) {
       return res.json({
         _id: user._id,
         username: user.username,
         email: user.email,
         token: generateToken(user._id),
       });
    }
    return res.status(401).json({ message: 'Invalid email or password' });
  }

  const user = await User.findOne({ email });

  if (user && (await bcrypt.compare(password, user.password))) {
    res.json({
      _id: user._id,
      username: user.username,
      email: user.email,
      token: generateToken(user._id),
    });
  } else {
    res.status(401).json({ message: 'Invalid email or password' });
  }
};
