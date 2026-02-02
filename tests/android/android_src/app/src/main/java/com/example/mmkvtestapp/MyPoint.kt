package com.example.mmkvtestapp

import android.os.Parcelable
import kotlinx.parcelize.Parcelize

@Parcelize
data class MyPoint(val x: Int, val y: Int) : Parcelable